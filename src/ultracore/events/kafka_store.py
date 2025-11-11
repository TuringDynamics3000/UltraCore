"""
Kafka Event Store

Wrapper around Kafka producer for backward compatibility
"""

from ultracore.events.kafka_producer import get_kafka_producer


def get_production_kafka_store():
    """Get Kafka event store (backward compatibility)"""
    return get_kafka_producer()
