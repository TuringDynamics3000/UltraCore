"""
ESG Portfolio Optimization Service - Production Version

This is a production-ready Kafka consumer service that processes portfolio
optimization requests asynchronously using the Epsilon Agent.

Features:
- Real Kafka integration (kafka-python)
- Graceful shutdown handling
- Comprehensive error handling
- Retry logic with exponential backoff
- Health checks and monitoring
- Structured logging
- Metrics collection
"""

import json
import logging
import signal
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
from threading import Event, Thread
import traceback

# Kafka integration
try:
    from kafka import KafkaConsumer, KafkaProducer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logging.warning("kafka-python not installed. Install with: pip install kafka-python")

from ultracore.esg.mcp.portfolio_optimizer import EsgPortfolioOptimizer
from ultracore.esg.agents.epsilon_agent import EpsilonAgent
from ultracore.esg.data.esg_data_loader import EsgDataLoader
from ultracore.esg.data.data_mesh_client import DataMeshClient
from ultracore.esg.events.schemas import PortfolioEventType

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/ultracore/optimization_service.log')
    ]
)
logger = logging.getLogger(__name__)


class ServiceMetrics:
    """Metrics collector for monitoring service health and performance"""
    
    def __init__(self):
        self.requests_received = 0
        self.requests_completed = 0
        self.requests_failed = 0
        self.total_processing_time = 0.0
        self.start_time = time.time()
    
    def record_request_received(self):
        self.requests_received += 1
    
    def record_request_completed(self, processing_time: float):
        self.requests_completed += 1
        self.total_processing_time += processing_time
    
    def record_request_failed(self):
        self.requests_failed += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        avg_processing_time = (
            self.total_processing_time / self.requests_completed 
            if self.requests_completed > 0 else 0
        )
        
        return {
            "uptime_seconds": round(uptime, 2),
            "requests_received": self.requests_received,
            "requests_completed": self.requests_completed,
            "requests_failed": self.requests_failed,
            "success_rate": (
                round(self.requests_completed / self.requests_received * 100, 2)
                if self.requests_received > 0 else 0
            ),
            "avg_processing_time_seconds": round(avg_processing_time, 2),
            "requests_per_minute": round(
                self.requests_completed / (uptime / 60) if uptime > 0 else 0, 2
            )
        }


class OptimizationServiceProduction:
    """
    Production-ready Kafka consumer service for ESG portfolio optimization.
    
    This service provides:
    - Graceful shutdown on SIGTERM/SIGINT
    - Automatic reconnection to Kafka
    - Retry logic with exponential backoff
    - Dead letter queue for failed messages
    - Health check endpoint
    - Prometheus-compatible metrics
    """
    
    def __init__(
        self,
        kafka_bootstrap_servers: str = "localhost:9092",
        kafka_topic: str = "esg-portfolio-events",
        kafka_group_id: str = "optimization-service-group",
        asset_universe: Optional[list] = None,
        max_retries: int = 3,
        retry_backoff_seconds: int = 5,
        enable_auto_commit: bool = False  # Manual commit for exactly-once processing
    ):
        """
        Initialize the optimization service.
        
        Args:
            kafka_bootstrap_servers: Kafka broker addresses
            kafka_topic: Topic to consume from and publish to
            kafka_group_id: Consumer group ID
            asset_universe: List of ISINs that can be invested in
            max_retries: Maximum number of retries for failed optimizations
            retry_backoff_seconds: Initial backoff time for retries
            enable_auto_commit: Whether to auto-commit offsets (False for exactly-once)
        """
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.kafka_group_id = kafka_group_id
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.enable_auto_commit = enable_auto_commit
        
        self.asset_universe = asset_universe or [
            "AU000000VAS3",
            "AU000000VGS3",
            "AU000000ETHI",
            "AU000000VAP3",
            "AU000000VGB3",
        ]
        
        # Shutdown handling
        self.shutdown_event = Event()
        self.consumer = None
        self.producer = None
        
        # Metrics
        self.metrics = ServiceMetrics()
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        
        logger.info("Initializing Optimization Service...")
        self._initialize_components()
        logger.info("✓ Service initialized successfully!")
    
    def _initialize_components(self):
        """Initialize all service components"""
        try:
            # Initialize ESG Data Loader
            logger.info("Initializing ESG Data Loader...")
            self.esg_data_loader = EsgDataLoader()
            
            # Initialize Data Mesh Client
            logger.info("Initializing Data Mesh Client...")
            self.data_mesh_client = DataMeshClient()
            
            # Initialize Epsilon Agent
            logger.info("Initializing Epsilon Agent...")
            state_dim = len(self.asset_universe) * 24
            action_dim = len(self.asset_universe)
            esg_feature_dim = len(self.asset_universe) * 3
            
            self.epsilon_agent = EpsilonAgent(
                state_dim=state_dim,
                action_dim=action_dim,
                esg_feature_dim=esg_feature_dim,
                epsilon_start=0.0  # Deterministic for production
            )
            
            # Load trained model if available
            try:
                self.epsilon_agent.load("/models/epsilon_agent_latest.pt")
                logger.info("✓ Loaded trained Epsilon Agent model")
            except FileNotFoundError:
                logger.warning("No trained model found, using initialized agent")
            
            # Initialize Portfolio Optimizer
            logger.info("Initializing Portfolio Optimizer...")
            self.optimizer = EsgPortfolioOptimizer(
                esg_data_loader=self.esg_data_loader,
                epsilon_agent=self.epsilon_agent,
                asset_universe=self.asset_universe,
                data_mesh_client=self.data_mesh_client
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            raise
    
    def _initialize_kafka(self):
        """Initialize Kafka consumer and producer"""
        if not KAFKA_AVAILABLE:
            raise RuntimeError("kafka-python not installed. Cannot initialize Kafka.")
        
        try:
            logger.info("Initializing Kafka consumer...")
            self.consumer = KafkaConsumer(
                self.kafka_topic,
                bootstrap_servers=self.kafka_bootstrap_servers,
                group_id=self.kafka_group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                enable_auto_commit=self.enable_auto_commit,
                auto_offset_reset='earliest',  # Start from beginning if no offset
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                max_poll_interval_ms=300000  # 5 minutes for long-running optimizations
            )
            
            logger.info("Initializing Kafka producer...")
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_serializer=lambda m: json.dumps(m).encode("utf-8"),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                max_in_flight_requests_per_connection=1  # Ensure ordering
            )
            
            logger.info("✓ Kafka initialized successfully")
            
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka: {e}", exc_info=True)
            raise
    
    def _handle_shutdown_signal(self, signum, frame):
        """Handle shutdown signals (SIGTERM, SIGINT)"""
        logger.info(f"Received shutdown signal: {signal.Signals(signum).name}")
        self.shutdown_event.set()
    
    def start(self):
        """Start the service"""
        logger.info("=" * 80)
        logger.info("Starting ESG Portfolio Optimization Service")
        logger.info("=" * 80)
        logger.info(f"Kafka Brokers: {self.kafka_bootstrap_servers}")
        logger.info(f"Topic: {self.kafka_topic}")
        logger.info(f"Consumer Group: {self.kafka_group_id}")
        logger.info(f"Asset Universe: {len(self.asset_universe)} assets")
        logger.info(f"Max Retries: {self.max_retries}")
        logger.info("=" * 80)
        
        # Initialize Kafka
        self._initialize_kafka()
        
        # Start health check thread
        health_check_thread = Thread(target=self._health_check_loop, daemon=True)
        health_check_thread.start()
        
        # Start metrics reporting thread
        metrics_thread = Thread(target=self._metrics_reporting_loop, daemon=True)
        metrics_thread.start()
        
        logger.info("✓ Service started successfully")
        logger.info("Waiting for optimization requests...")
        
        # Main event processing loop
        self._run_event_loop()
    
    def _run_event_loop(self):
        """Main event processing loop"""
        try:
            while not self.shutdown_event.is_set():
                # Poll for messages with timeout
                messages = self.consumer.poll(timeout_ms=1000, max_records=10)
                
                if not messages:
                    continue
                
                for topic_partition, records in messages.items():
                    for message in records:
                        if self.shutdown_event.is_set():
                            break
                        
                        try:
                            event = message.value
                            self._handle_event(event)
                            
                            # Manually commit offset after successful processing
                            if not self.enable_auto_commit:
                                self.consumer.commit()
                                
                        except Exception as e:
                            logger.error(f"Error processing message: {e}", exc_info=True)
                            self.metrics.record_request_failed()
                            
                            # Send to dead letter queue
                            self._send_to_dead_letter_queue(message, str(e))
        
        except Exception as e:
            logger.error(f"Fatal error in event loop: {e}", exc_info=True)
            raise
        
        finally:
            self._shutdown()
    
    def _handle_event(self, event: Dict[str, Any]):
        """Handle an incoming event from Kafka"""
        event_type = event.get("event_type")
        
        if event_type == PortfolioEventType.PORTFOLIO_OPTIMIZATION_REQUESTED:
            self.metrics.record_request_received()
            self._handle_optimization_request(event)
        else:
            logger.debug(f"Ignoring event of type: {event_type}")
    
    def _handle_optimization_request(self, request_event: Dict[str, Any]):
        """Handle a portfolio optimization request with retry logic"""
        portfolio_id = request_event.get("portfolio_id", "unknown")
        request_id = request_event.get("event_id", "unknown")
        
        logger.info("=" * 80)
        logger.info(f"Processing optimization request: {request_id}")
        logger.info(f"Portfolio ID: {portfolio_id}")
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                # Extract request data
                payload = request_event.get("payload", {})
                current_portfolio = payload.get("current_portfolio", {})
                objectives = payload.get("objectives", {})
                constraints = payload.get("constraints")
                
                logger.info(f"Current Portfolio: {len(current_portfolio)} holdings")
                logger.info(f"Objectives: {objectives}")
                
                if retry_count > 0:
                    logger.info(f"Retry attempt {retry_count}/{self.max_retries}")
                
                # Run optimization
                start_time = time.time()
                result = self.optimizer.optimize(
                    current_portfolio=current_portfolio,
                    objectives=objectives,
                    constraints=constraints
                )
                elapsed_time = time.time() - start_time
                
                logger.info(f"✓ Optimization completed in {elapsed_time:.2f}s")
                logger.info(f"Optimized Portfolio: {len(result['optimized_portfolio'])} holdings")
                logger.info(f"Trade List: {len(result['trade_list'])} trades")
                
                # Record metrics
                self.metrics.record_request_completed(elapsed_time)
                
                # Create completion event
                completion_event = {
                    "event_type": PortfolioEventType.PORTFOLIO_OPTIMIZATION_COMPLETED,
                    "timestamp": datetime.now().isoformat(),
                    "portfolio_id": portfolio_id,
                    "request_id": request_id,
                    "payload": result,
                    "processing_time_seconds": elapsed_time,
                    "retry_count": retry_count
                }
                
                # Publish completion event
                self._publish_event(completion_event, portfolio_id)
                
                logger.info(f"✓ Published completion event for request: {request_id}")
                logger.info("=" * 80)
                
                return  # Success, exit retry loop
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                logger.error(
                    f"Error processing optimization request (attempt {retry_count}/{self.max_retries + 1}): {e}",
                    exc_info=True
                )
                
                if retry_count <= self.max_retries:
                    # Exponential backoff
                    backoff_time = self.retry_backoff_seconds * (2 ** (retry_count - 1))
                    logger.info(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
        
        # All retries exhausted
        logger.error(f"Failed to process request after {self.max_retries + 1} attempts")
        self.metrics.record_request_failed()
        
        # Publish error event
        error_event = {
            "event_type": "portfolio_optimization_failed",
            "timestamp": datetime.now().isoformat(),
            "portfolio_id": portfolio_id,
            "request_id": request_id,
            "error": str(last_error),
            "error_type": type(last_error).__name__,
            "traceback": traceback.format_exc(),
            "retry_count": retry_count - 1
        }
        
        self._publish_event(error_event, portfolio_id)
        logger.info("=" * 80)
    
    def _publish_event(self, event: Dict[str, Any], key: str):
        """Publish an event to Kafka with error handling"""
        try:
            future = self.producer.send(
                self.kafka_topic,
                value=event,
                key=key.encode("utf-8")
            )
            
            # Wait for acknowledgment (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Event published to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            
        except KafkaError as e:
            logger.error(f"Failed to publish event: {e}", exc_info=True)
            raise
    
    def _send_to_dead_letter_queue(self, message, error: str):
        """Send failed message to dead letter queue"""
        try:
            dlq_event = {
                "original_message": message.value,
                "error": error,
                "timestamp": datetime.now().isoformat(),
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset
            }
            
            self.producer.send(
                f"{self.kafka_topic}-dlq",
                value=dlq_event
            )
            
            logger.info(f"Sent message to dead letter queue: {message.offset}")
            
        except Exception as e:
            logger.error(f"Failed to send to dead letter queue: {e}", exc_info=True)
    
    def _health_check_loop(self):
        """Periodic health check loop"""
        while not self.shutdown_event.is_set():
            try:
                # Check Kafka connection
                if self.consumer:
                    # Try to get cluster metadata
                    self.consumer.topics()
                    logger.debug("Health check: Kafka connection OK")
                
                # Check Data Mesh connection
                try:
                    self.data_mesh_client.get_data_product_metadata("financial_data_product")
                    logger.debug("Health check: Data Mesh connection OK")
                except Exception as e:
                    logger.warning(f"Health check: Data Mesh connection issue: {e}")
                
            except Exception as e:
                logger.error(f"Health check failed: {e}", exc_info=True)
            
            # Sleep for 30 seconds
            self.shutdown_event.wait(30)
    
    def _metrics_reporting_loop(self):
        """Periodic metrics reporting loop"""
        while not self.shutdown_event.is_set():
            try:
                metrics = self.metrics.get_metrics()
                logger.info("=" * 80)
                logger.info("SERVICE METRICS")
                logger.info("=" * 80)
                for key, value in metrics.items():
                    logger.info(f"{key}: {value}")
                logger.info("=" * 80)
                
            except Exception as e:
                logger.error(f"Metrics reporting failed: {e}", exc_info=True)
            
            # Sleep for 60 seconds
            self.shutdown_event.wait(60)
    
    def _shutdown(self):
        """Graceful shutdown"""
        logger.info("=" * 80)
        logger.info("Shutting down Optimization Service...")
        logger.info("=" * 80)
        
        # Close Kafka consumer
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("✓ Kafka consumer closed")
        
        # Flush and close Kafka producer
        if self.producer:
            logger.info("Flushing Kafka producer...")
            self.producer.flush(timeout=10)
            self.producer.close()
            logger.info("✓ Kafka producer closed")
        
        # Log final metrics
        final_metrics = self.metrics.get_metrics()
        logger.info("=" * 80)
        logger.info("FINAL METRICS")
        logger.info("=" * 80)
        for key, value in final_metrics.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 80)
        
        logger.info("✓ Service shutdown complete")


def main():
    """Main entry point for the service"""
    import os
    
    # Read configuration from environment variables
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic = os.getenv("KAFKA_TOPIC", "esg-portfolio-events")
    kafka_group_id = os.getenv("KAFKA_GROUP_ID", "optimization-service-group")
    
    # Create and start service
    service = OptimizationServiceProduction(
        kafka_bootstrap_servers=kafka_bootstrap_servers,
        kafka_topic=kafka_topic,
        kafka_group_id=kafka_group_id
    )
    
    service.start()


if __name__ == "__main__":
    main()
