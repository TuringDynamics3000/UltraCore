"""
ESG Event Producer

This module provides a Kafka producer for publishing ESG events to the appropriate topics.
"""

import json
from datetime import datetime
from typing import Any, Dict
from dataclasses import asdict

# Note: In production, you would use kafka-python or confluent-kafka
# For now, we'll create a mock producer that can be easily replaced

class EsgEventProducer:
    """
    Producer for ESG events to Kafka topics.
    
    This is a mock implementation that logs events. In production, this would
    be replaced with a real Kafka producer using kafka-python or confluent-kafka.
    """
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.events_log = []  # For testing/development
        
    def _serialize_event(self, event: Any) -> str:
        """Serialize an event dataclass to JSON"""
        event_dict = asdict(event)
        # Convert datetime objects to ISO format strings
        for key, value in event_dict.items():
            if isinstance(value, datetime):
                event_dict[key] = value.isoformat()
        return json.dumps(event_dict)
    
    def publish(self, topic: str, event: Any, key: str = None) -> None:
        """
        Publish an event to a Kafka topic.
        
        Args:
            topic: The Kafka topic name
            event: The event dataclass to publish
            key: Optional partition key
        """
        serialized_event = self._serialize_event(event)
        
        # Mock implementation: log the event
        self.events_log.append({
            "topic": topic,
            "key": key,
            "value": serialized_event,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"[ESG Event Published] Topic: {topic}, Key: {key}")
        print(f"  Event: {serialized_event[:200]}...")  # First 200 chars
        
        # In production, this would be:
        # self.producer.send(topic, key=key, value=serialized_event)
        
    def flush(self) -> None:
        """Flush any pending events"""
        # In production: self.producer.flush()
        pass
    
    def close(self) -> None:
        """Close the producer"""
        # In production: self.producer.close()
        pass


# Singleton instance
_producer_instance = None

def get_esg_producer() -> EsgEventProducer:
    """Get or create the singleton ESG event producer"""
    global _producer_instance
    if _producer_instance is None:
        _producer_instance = EsgEventProducer()
    return _producer_instance
