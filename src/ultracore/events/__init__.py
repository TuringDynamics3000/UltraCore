"""
UltraCore Events Module

Kafka-first event sourcing infrastructure
"""

from ultracore.events.kafka_producer import (
    KafkaEventProducer,
    EventTopic,
    get_kafka_producer,
    close_kafka_producer
)

__all__ = [
    'KafkaEventProducer',
    'EventTopic',
    'get_kafka_producer',
    'close_kafka_producer'
]
