# UltraCore - Kafka-First Event Sourcing

## 🏗️ Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    KAFKA-FIRST ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

WRITE PATH (Commands):
  API Request → Manager → Kafka Producer → Kafka Topics
                                            (source of truth)

READ PATH (Queries):
  API Request → Repository → PostgreSQL → Response
                              (materialized view)

MATERIALIZATION:
  Kafka Topics → Consumers → PostgreSQL
  (async, exactly-once)

EVENT REPLAY:
  Kafka Topics → Replay Service → Rebuild PostgreSQL
  (disaster recovery, testing)
```

## 🎯 Key Principles

### 1. Kafka = Source of Truth
- ALL state changes written to Kafka first
- Immutable event log
- Guaranteed ordering per aggregate
- Event replay capability

### 2. PostgreSQL = Materialized View
- Optimized for queries
- Built from Kafka events
- Can be rebuilt anytime
- Eventually consistent

### 3. Exactly-Once Semantics
- Idempotent consumers
- Processed events tracking
- No duplicate processing

### 4. CQRS (Command Query Responsibility Segregation)
- Write model: Kafka events
- Read model: PostgreSQL tables
- Separate optimization

## 🚀 Quick Start

### Option 1: Full Stack (Recommended)
```powershell
# Start everything (Kafka, DB, Consumers, API)
.\start_all.ps1
```

### Option 2: Step-by-Step
```powershell
# 1. Start infrastructure
docker-compose up -d

# 2. Initialize database
python init_db.py

# 3. Start consumers (separate terminal)
.\start_consumers.ps1

# 4. Start API
python run.py
```

## 📊 Monitoring

### Kafka UI
http://localhost:8080

View:
- Topics and partitions
- Consumer groups and lag
- Message browser
- Schema registry

### API Docs
http://localhost:8000/api/v1/docs

Test:
- Create customer (writes to Kafka)
- Get customer (reads from PostgreSQL)
- View materialization

### Database
```sql
-- View processed events (idempotency tracking)
SELECT * FROM processed_events ORDER BY processed_at DESC LIMIT 10;

-- View materialized customers
SELECT * FROM customers.customers LIMIT 10;

-- View materialized accounts
SELECT * FROM accounts.accounts LIMIT 10;
```

## 🔄 Event Flow Example

### Create Customer

1. **API Request**
```
   POST /api/v1/customers
   { "first_name": "John", "last_name": "Doe", ... }
```

2. **Manager Creates Event**
```python
   await kafka_producer.publish_event(
       topic=EventTopic.CUSTOMER_EVENTS,
       event_type="CustomerCreated",
       event_data={...}
   )
```

3. **Kafka Stores Event**
```
   Topic: ultracore.customers.events
   Partition: 3 (by customer_id)
   Offset: 12847
```

4. **Consumer Materializes**
```python
   # Consumer reads event from Kafka
   # Creates Customer in PostgreSQL
   customer = Customer(**event_data)
   session.add(customer)
```

5. **API Response**
```
   201 Created
   { "customer_id": "CUST-001", ... }
```

## 🔁 Event Replay

### Rebuild Database from Kafka
```python
# Stop consumers
# Drop and recreate database
python init_db.py

# Reset consumer offsets to beginning
# Start consumers (will replay all events)
.\start_consumers.ps1
```

This rebuilds the entire PostgreSQL database from Kafka!

## 📈 Scaling

### Horizontal Scaling
```yaml
# Add more consumer instances
docker-compose scale consumer=3

# Kafka automatically balances partitions
# Each partition processed by one consumer
```

### Performance Tuning
```python
# Producer settings
acks='all'  # Durability (slower)
acks=1      # Performance (faster)

# Consumer settings
batch_size=100   # Messages per batch
fetch_max_wait_ms=500  # Latency vs throughput
```

## 🧪 Testing

### Test Event Production
```python
from ultracore.events.kafka_producer import get_kafka_producer, EventTopic

producer = get_kafka_producer()

await producer.publish_event(
    topic=EventTopic.CUSTOMER_EVENTS,
    event_type="CustomerCreated",
    aggregate_type="Customer",
    aggregate_id="CUST-TEST-001",
    event_data={"first_name": "Test"},
    tenant_id="DEFAULT",
    user_id="test-user"
)
```

### Verify in Kafka UI
1. Go to http://localhost:8080
2. Click "Topics"
3. Click "ultracore.customers.events"
4. View messages

### Verify in PostgreSQL
```sql
-- Should appear after ~1 second
SELECT * FROM customers.customers WHERE customer_id = 'CUST-TEST-001';

-- Check processed events
SELECT * FROM processed_events WHERE aggregate_id = 'CUST-TEST-001';
```

## 🎯 Benefits

### 1. True Event Sourcing
- Complete audit trail
- Time travel (replay to any point)
- Event-driven architecture

### 2. Reliability
- Kafka durability (replication)
- Exactly-once processing
- Disaster recovery

### 3. Performance
- Write optimized (Kafka)
- Read optimized (PostgreSQL)
- Async materialization

### 4. Scalability
- Kafka handles high throughput
- Independent scaling
- Partition-based parallelism

### 5. Flexibility
- Multiple consumers (different views)
- Real-time analytics
- Event-driven integrations

## 📚 Learn More

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
