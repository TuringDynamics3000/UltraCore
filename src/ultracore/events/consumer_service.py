"""
UltraCore Consumer Service

Runs all Kafka consumers to materialize events to PostgreSQL

Usage:
    python -m ultracore.events.consumer_service
"""

import asyncio
import logging
import signal
from typing import List

from ultracore.events.kafka_consumer import KafkaEventConsumer
from ultracore.events.customer_event_handler import get_customer_handlers
from ultracore.events.account_event_handler import get_account_handlers
from ultracore.events.kafka_producer import EventTopic

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsumerService:
    """
    Consumer service orchestrator
    
    Manages multiple Kafka consumers for different topics
    """
    
    def __init__(self):
        self.consumers: List[KafkaEventConsumer] = []
        self.running = False
    
    def initialize_consumers(self):
        """Initialize all consumers"""
        
        logger.info("🔄 Initializing Kafka consumers...")
        
        # Customer events consumer
        customer_consumer = KafkaEventConsumer(
            topic=EventTopic.CUSTOMER_EVENTS.value,
            group_id="ultracore-customer-consumer",
            event_handlers=get_customer_handlers()
        )
        self.consumers.append(customer_consumer)
        
        # Account events consumer
        account_consumer = KafkaEventConsumer(
            topic=EventTopic.ACCOUNT_EVENTS.value,
            group_id="ultracore-account-consumer",
            event_handlers=get_account_handlers()
        )
        self.consumers.append(account_consumer)
        
        # Transaction events consumer (same handlers as accounts)
        transaction_consumer = KafkaEventConsumer(
            topic=EventTopic.TRANSACTION_EVENTS.value,
            group_id="ultracore-transaction-consumer",
            event_handlers=get_account_handlers()
        )
        self.consumers.append(transaction_consumer)
        
        logger.info(f"✓ Initialized {len(self.consumers)} consumers")
    
    async def start(self):
        """Start all consumers"""
        self.running = True
        
        logger.info("🚀 Starting consumer service...")
        logger.info("=" * 70)
        
        # Start all consumers concurrently
        tasks = [
            asyncio.create_task(consumer.start())
            for consumer in self.consumers
        ]
        
        # Wait for all consumers
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Consumer service error: {e}", exc_info=True)
        finally:
            logger.info("🛑 Consumer service stopped")
    
    def stop(self):
        """Stop all consumers"""
        logger.info("🛑 Stopping consumer service...")
        self.running = False
        
        for consumer in self.consumers:
            consumer.stop()


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║           UltraCore Banking Platform                             ║
    ║           Kafka Event Consumer Service                           ║
    ║                                                                  ║
    ║           Kafka-First Event Sourcing Architecture                ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize service
    service = ConsumerService()
    service.initialize_consumers()
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n🛑 Shutdown signal received...")
        service.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start consuming
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
