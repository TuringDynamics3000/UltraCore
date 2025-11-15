# UltraCore ESG Module - Quick Reference Guide

## 🚀 Quick Start

### Install Dependencies
```bash
pip install kafka-python torch pandas numpy
```

### Run Optimization Service
```bash
python -m ultracore.esg.services.optimization_service_production
```

### Use MCP Tools
```python
from ultracore.esg import EsgMcpTools, EsgDataLoader, EpsilonAgent

# Initialize
loader = EsgDataLoader()
agent = EpsilonAgent(state_dim=120, action_dim=5, esg_feature_dim=15)
tools = EsgMcpTools(loader, agent, asset_universe=["AU000000VAS3", ...])

# Optimize portfolio
result = tools.optimize_portfolio_esg(
    current_portfolio={"AU000000VAS3": 0.7, "AU000000VGS3": 0.3},
    objectives={"target_return": 0.10, "esg_weight": 0.4}
)
```

---

## 📁 File Structure

```
src/ultracore/esg/
├── agents/
│   ├── epsilon_agent.py          # RL agent for ESG optimization
│   └── esg_portfolio_env.py      # Gymnasium environment
├── data/
│   ├── esg_data_loader.py        # ESG data access
│   └── data_mesh_client.py       # Data Mesh integration
├── events/
│   ├── schemas.py                # Event type definitions
│   └── producer.py               # Kafka producer
├── mcp/
│   ├── esg_tools.py              # MCP tool implementations
│   └── portfolio_optimizer.py    # Portfolio optimization logic
└── services/
    └── optimization_service_production.py  # Kafka consumer service
```

---

## 🔧 Key Classes

### EpsilonAgent
```python
agent = EpsilonAgent(
    state_dim=120,        # 20 returns × 5 assets + 5 holdings + 15 ESG features
    action_dim=5,         # 5 assets
    esg_feature_dim=15    # 3 ESG metrics × 5 assets
)

# Select action
action = agent.select_action(state, esg_constraints)

# Train
agent.train(state, action, reward, next_state, done)

# Save/Load
agent.save("/models/epsilon_agent.pt")
agent.load("/models/epsilon_agent.pt")
```

### EsgPortfolioOptimizer
```python
optimizer = EsgPortfolioOptimizer(
    esg_data_loader=loader,
    epsilon_agent=agent,
    asset_universe=["AU000000VAS3", "AU000000VGS3", ...],
    lookback_days=252
)

result = optimizer.optimize(
    current_portfolio={"AU000000VAS3": 0.7},
    objectives={"target_return": 0.10, "esg_weight": 0.4},
    constraints={"min_esg_rating": "A"}
)
```

### OptimizationServiceProduction
```python
service = OptimizationServiceProduction(
    kafka_bootstrap_servers="localhost:9092",
    kafka_topic="esg-portfolio-events",
    kafka_group_id="optimization-service-group"
)

service.start()  # Blocks until shutdown signal
```

---

## 📊 Event Schemas

### PortfolioOptimizationRequested
```json
{
  "event_type": "portfolio_optimization_requested",
  "event_id": "req-001",
  "portfolio_id": "portfolio-001",
  "timestamp": "2025-11-15T00:00:00Z",
  "payload": {
    "current_portfolio": {"AU000000VAS3": 0.7, "AU000000VGS3": 0.3},
    "objectives": {
      "target_return": 0.10,
      "max_volatility": 0.15,
      "esg_weight": 0.4,
      "min_esg_rating": "A",
      "max_carbon_intensity": 100.0
    }
  }
}
```

### PortfolioOptimizationCompleted
```json
{
  "event_type": "portfolio_optimization_completed",
  "portfolio_id": "portfolio-001",
  "request_id": "req-001",
  "timestamp": "2025-11-15T00:00:01Z",
  "payload": {
    "optimized_portfolio": {"AU000000ETHI": 1.0},
    "current_metrics": {...},
    "optimized_metrics": {...},
    "improvement": {...},
    "trade_list": [...]
  },
  "processing_time_seconds": 0.64
}
```

---

## 🐳 Docker Commands

### Build Image
```bash
docker build -t ultracore-esg-optimization-service:latest \
  -f Dockerfile.optimization_service .
```

### Run Container
```bash
docker run -d \
  --name optimization-service \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  -e KAFKA_TOPIC=esg-portfolio-events \
  -v /models:/models:ro \
  ultracore-esg-optimization-service:latest
```

### View Logs
```bash
docker logs -f optimization-service
```

---

## ☸️ Kubernetes Commands

### Deploy
```bash
kubectl apply -f k8s/optimization-service-deployment.yaml
```

### Check Status
```bash
kubectl get pods -n ultracore-esg
kubectl describe pod -n ultracore-esg <pod-name>
```

### View Logs
```bash
kubectl logs -f -n ultracore-esg deployment/optimization-service
```

### Scale
```bash
kubectl scale deployment optimization-service -n ultracore-esg --replicas=10
```

### Port Forward (for testing)
```bash
kubectl port-forward -n ultracore-esg deployment/optimization-service 8080:8080
```

---

## 📈 Monitoring

### Prometheus Metrics
```
# Request rate
rate(optimization_requests_total[5m])

# Success rate
optimization_requests_completed / optimization_requests_total

# Latency
histogram_quantile(0.95, optimization_processing_seconds_bucket)

# Queue depth
kafka_consumer_lag{topic="esg-portfolio-events"}
```

### Grafana Dashboard
- Import dashboard ID: `ultracore-esg-optimization`
- Panels: Request rate, success rate, latency (P50/P95/P99), queue depth, error rate

---

## 🧪 Testing

### Unit Tests
```bash
pytest tests/esg/test_epsilon_agent.py
pytest tests/esg/test_portfolio_optimizer.py
```

### Integration Tests
```bash
python test_optimization_service.py
```

### Load Tests
```bash
# Using locust
locust -f tests/load/test_optimization_load.py --host=http://localhost:8080
```

---

## 🔍 Debugging

### Check Kafka Consumer Lag
```bash
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group optimization-service-group --describe
```

### View Dead Letter Queue
```bash
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic esg-portfolio-events-dlq --from-beginning
```

### Tail Service Logs
```bash
tail -f /var/log/ultracore/optimization_service.log
```

### Check Data Mesh Connectivity
```python
from ultracore.esg.data.data_mesh_client import DataMeshClient

client = DataMeshClient()
metadata = client.get_data_product_metadata("financial_data_product")
print(metadata)
```

---

## 🚨 Common Issues

### Issue: Kafka connection refused
**Solution:** Check `KAFKA_BOOTSTRAP_SERVERS` environment variable and ensure Kafka is running.

### Issue: Model not found
**Solution:** Ensure trained model exists at `/models/epsilon_agent_latest.pt` or update path in service initialization.

### Issue: High consumer lag
**Solution:** Scale up replicas with `kubectl scale` or increase Kafka partitions.

### Issue: Out of memory
**Solution:** Increase resource limits in Kubernetes deployment or reduce batch size.

---

## 📚 Additional Resources

- **Full Documentation:** `ESG_MODULE_COMPLETE.md`
- **Deployment Guide:** `ESG_DEPLOYMENT_GUIDE.md`
- **Integration Plan:** `ESG_OPTIMIZATION_INTEGRATION_PLAN.md`
- **API Reference:** `src/ultracore/esg/README.md`
- **Architecture Design:** `ULTRACARE_ESG_MODULE_DESIGN.md`

---

## 💬 Support

- **GitHub Issues:** https://github.com/mjmilne1/UltraCore/issues
- **Documentation:** https://ultracore.readthedocs.io
- **Slack:** #ultracore-esg
