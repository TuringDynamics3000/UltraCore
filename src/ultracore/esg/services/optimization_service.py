"""
ESG Portfolio Optimization Service

This service is a long-running Kafka consumer that listens for portfolio
optimization requests and processes them asynchronously using the Epsilon Agent.

It demonstrates the power of event-driven architecture:
- Decoupled from the MCP tool (no blocking)
- Horizontally scalable (add more instances)
- Resilient (can replay events from Kafka)
- Auditable (all requests and results are events)
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time

# Note: kafka-python would be used in production
# For now, we'll create a mock implementation that can be easily replaced

from ultracore.esg.mcp.portfolio_optimizer import EsgPortfolioOptimizer
from ultracore.esg.agents.epsilon_agent import EpsilonAgent
from ultracore.esg.data.esg_data_loader import EsgDataLoader
from ultracore.esg.events.producer import get_esg_producer
from ultracore.esg.events.schemas import PortfolioEventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizationService:
    """
    Kafka consumer service for processing portfolio optimization requests.
    
    This service:
    1. Consumes PortfolioOptimizationRequested events from Kafka
    2. Invokes the Epsilon Agent to optimize the portfolio
    3. Publishes PortfolioOptimizationCompleted events back to Kafka
    """
    
    def __init__(
        self,
        kafka_bootstrap_servers: str = "localhost:9092",
        kafka_topic: str = "esg-portfolio-events",
        asset_universe: Optional[list] = None
    ):
        """
        Initialize the optimization service.
        
        Args:
            kafka_bootstrap_servers: Kafka broker addresses
            kafka_topic: Topic to consume from and publish to
            asset_universe: List of ISINs that can be invested in
        """
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.asset_universe = asset_universe or [
            "AU000000VAS3",
            "AU000000VGS3",
            "AU000000ETHI",
            "AU000000VAP3",
            "AU000000VGB3",
        ]
        
        # Initialize components
        logger.info("Initializing ESG Data Loader...")
        self.esg_data_loader = EsgDataLoader()
        
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
        
        logger.info("Initializing Portfolio Optimizer...")
        self.optimizer = EsgPortfolioOptimizer(
            esg_data_loader=self.esg_data_loader,
            epsilon_agent=self.epsilon_agent,
            asset_universe=self.asset_universe
        )
        
        # Get event producer
        self.producer = get_esg_producer()
        
        # Mock Kafka consumer (in production, use kafka-python)
        self.consumer = None
        self.running = False
        
        logger.info("✓ Optimization Service initialized successfully!")
    
    def start(self):
        """Start the service (begin consuming events)"""
        logger.info(f"Starting Optimization Service...")
        logger.info(f"  Kafka Brokers: {self.kafka_bootstrap_servers}")
        logger.info(f"  Topic: {self.kafka_topic}")
        logger.info(f"  Asset Universe: {len(self.asset_universe)} assets")
        
        self.running = True
        
        # In production, this would be:
        # self.consumer = KafkaConsumer(
        #     self.kafka_topic,
        #     bootstrap_servers=self.kafka_bootstrap_servers,
        #     value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        #     group_id="optimization-service-group"
        # )
        
        logger.info("✓ Service started. Waiting for optimization requests...")
        
        # Mock event loop (in production, this would consume from Kafka)
        self._run_event_loop()
    
    def _run_event_loop(self):
        """Main event processing loop"""
        # In production, this would be:
        # for message in self.consumer:
        #     event = message.value
        #     self.handle_event(event)
        
        # For demo purposes, we'll just log that we're ready
        logger.info("Event loop running. Service is ready to process requests.")
        logger.info("(In production, this would consume from Kafka)")
        
        # Keep the service alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down service...")
            self.stop()
    
    def handle_event(self, event: Dict[str, Any]):
        """
        Handle an incoming event from Kafka.
        
        Args:
            event: The event dictionary
        """
        event_type = event.get("event_type")
        
        if event_type == PortfolioEventType.PORTFOLIO_OPTIMIZATION_REQUESTED:
            self.handle_optimization_request(event)
        else:
            logger.debug(f"Ignoring event of type: {event_type}")
    
    def handle_optimization_request(self, request_event: Dict[str, Any]):
        """
        Handle a portfolio optimization request.
        
        Args:
            request_event: The PortfolioOptimizationRequested event
        """
        portfolio_id = request_event.get("portfolio_id")
        request_id = request_event.get("event_id")
        
        logger.info(f"Processing optimization request: {request_id}")
        logger.info(f"  Portfolio ID: {portfolio_id}")
        
        try:
            # Extract request data
            payload = request_event.get("payload", {})
            current_portfolio = payload.get("current_portfolio", {})
            objectives = payload.get("objectives", {})
            constraints = payload.get("constraints")
            
            logger.info(f"  Current Portfolio: {len(current_portfolio)} holdings")
            logger.info(f"  Objectives: {objectives}")
            
            # Run optimization
            start_time = time.time()
            result = self.optimizer.optimize(
                current_portfolio=current_portfolio,
                objectives=objectives,
                constraints=constraints
            )
            elapsed_time = time.time() - start_time
            
            logger.info(f"✓ Optimization completed in {elapsed_time:.2f}s")
            logger.info(f"  Optimized Portfolio: {len(result['optimized_portfolio'])} holdings")
            logger.info(f"  Trade List: {len(result['trade_list'])} trades")
            
            # Create completion event
            completion_event = {
                "event_type": PortfolioEventType.PORTFOLIO_OPTIMIZATION_COMPLETED,
                "timestamp": datetime.now().isoformat(),
                "portfolio_id": portfolio_id,
                "request_id": request_id,
                "payload": result,
                "processing_time_seconds": elapsed_time
            }
            
            # Publish completion event
            self.producer.publish(
                topic=self.kafka_topic,
                event=completion_event,
                key=portfolio_id
            )
            
            logger.info(f"✓ Published completion event for request: {request_id}")
            
        except Exception as e:
            logger.error(f"Error processing optimization request: {e}", exc_info=True)
            
            # Publish error event
            error_event = {
                "event_type": "portfolio_optimization_failed",
                "timestamp": datetime.now().isoformat(),
                "portfolio_id": portfolio_id,
                "request_id": request_id,
                "error": str(e)
            }
            
            self.producer.publish(
                topic=self.kafka_topic,
                event=error_event,
                key=portfolio_id
            )
    
    def stop(self):
        """Stop the service"""
        logger.info("Stopping Optimization Service...")
        self.running = False
        
        if self.consumer:
            self.consumer.close()
        
        logger.info("✓ Service stopped")


def main():
    """Main entry point for the service"""
    service = OptimizationService()
    service.start()


if __name__ == "__main__":
    main()
