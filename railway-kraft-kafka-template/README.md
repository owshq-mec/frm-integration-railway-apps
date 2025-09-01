# 🚀 Railway KRaft Kafka Template

A production-ready Apache Kafka deployment using **KRaft mode** (no ZooKeeper) optimized for Railway platform with external TCP access.

## ✅ **Key Features**

- **KRaft Mode**: No ZooKeeper dependency - eliminates session instability
- **External Access**: Pre-configured for Railway TCP proxy
- **Production Ready**: Optimized memory and performance settings
- **Cost Effective**: 90% savings compared to managed Kafka services
- **Single Click Deploy**: Ready-to-use Railway template

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────┐
│           Railway Platform          │
│  ┌─────────────────────────────────┐ │
│  │        Kafka KRaft Node         │ │
│  │  ├─ Kafka Broker (Port 9092)    │ │
│  │  ├─ KRaft Controller (Port 9093)│ │
│  │  └─ JMX Metrics (Port 9999)     │ │
│  │                                 │ │
│  │  External Access:               │ │
│  │  └─ TCP Proxy → Port 9092       │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 🚀 **Quick Deploy to Railway**

### **Option 1: Deploy Button**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### **Option 2: Manual Deployment**
1. Fork this repository
2. Connect to Railway
3. Enable TCP proxy in Railway service settings
4. Deploy and get your external domain

---

## 🔧 **Local Testing**

### **Prerequisites**
- Docker and Docker Compose
- kcat (kafkacat) for testing

### **Run Locally**
```bash
# Clone the template
git clone <your-repo>
cd railway-kraft-kafka-template

# Start Kafka
docker-compose up --build

# Test connectivity
kcat -b localhost:9092 -L

# Send test message
echo '{"test": "kraft-local"}' | kcat -b localhost:9092 -t test-topic -P

# Consume messages
kcat -b localhost:9092 -t test-topic -C -o beginning -e
```

---

## 🌐 **External Access Configuration**

### **Railway Setup Steps**
1. **Deploy the template** to Railway
2. **Enable TCP Proxy** in service settings:
   ```
   Service Settings → Networking → Enable TCP Proxy
   ```
3. **Get your external domain**:
   ```
   Format: <service-name>.proxy.rlwy.net:<port>
   Example: kafka-kraft.proxy.rlwy.net:21412
   ```

### **Client Configuration**
```bash
# Your Railway Kafka endpoint
KAFKA_BOOTSTRAP_SERVERS="your-service.proxy.rlwy.net:PORT"

# Test external connectivity
kcat -b your-service.proxy.rlwy.net:PORT -L
```

---

## ⚙️ **Configuration**

### **Environment Variables**
| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_CLUSTER_ID` | KRaft cluster identifier | Auto-generated |
| `KAFKA_HEAP_OPTS` | JVM heap settings | `-Xmx512m -Xms512m` |
| `KAFKA_LOG_RETENTION_HOURS` | Message retention time | `168` (7 days) |
| `KAFKA_LOG_RETENTION_BYTES` | Maximum log size | `1073741824` (1GB) |
| `KAFKA_NUM_PARTITIONS` | Default partitions per topic | `3` |

### **Memory Optimization**
```bash
# Production (Railway)
KAFKA_HEAP_OPTS="-Xmx512m -Xms512m"

# Development (Local)
KAFKA_HEAP_OPTS="-Xmx256m -Xms256m"
```

---

## 🧪 **Testing Your Deployment**

### **1. Basic Connectivity**
```bash
# List topics and brokers
kcat -b your-kafka.proxy.rlwy.net:PORT -L

# Check cluster health
kcat -b your-kafka.proxy.rlwy.net:PORT -L | grep "broker"
```

### **2. Producer Test**
```bash
# Send test messages
for i in {1..5}; do
  echo "{\"id\":$i,\"message\":\"Test $i\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" | \
  kcat -b your-kafka.proxy.rlwy.net:PORT -t railway-test -P
done
```

### **3. Consumer Test**
```bash
# Consume all messages
kcat -b your-kafka.proxy.rlwy.net:PORT -t railway-test -C -o beginning -e

# Real-time monitoring
kcat -b your-kafka.proxy.rlwy.net:PORT -t railway-test -C -o end
```

---

## 📊 **Performance Characteristics**

### **Throughput**
- **Single Node**: 1000+ messages/second
- **Latency**: <100ms producer latency
- **Memory**: 512MB heap (Railway optimized)

### **Reliability**
- **No ZooKeeper**: Eliminates session issues
- **Auto-restart**: Railway handles container restarts
- **Health checks**: Built-in liveness probes

---

## 🔍 **Monitoring**

### **JMX Metrics**
```bash
# JMX endpoint (internal only)
KAFKA_JMX_PORT=9999

# Key metrics to monitor:
# - kafka.server:type=BrokerTopicMetrics
# - kafka.server:type=ReplicaManager
# - kafka.log:type=LogSize
```

### **Log Analysis**
```bash
# Railway logs
railway logs --service kafka-kraft

# Container logs (local)
docker-compose logs kafka-kraft
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. External Connection Failed**
```bash
# Verify TCP proxy is enabled
# Check Railway service settings

# Test internal connectivity first
railway shell
kafka-broker-api-versions --bootstrap-server localhost:9092
```

#### **2. Out of Memory**
```bash
# Reduce heap size for Railway limits
KAFKA_HEAP_OPTS="-Xmx256m -Xms256m"

# Or upgrade Railway plan
```

#### **3. Slow Startup**
```bash
# Normal KRaft startup takes 30-60 seconds
# Check logs for "Kafka Server started" message
```

### **Health Check Commands**
```bash
# 1. Service health
railway ps

# 2. Kafka health
kcat -b your-kafka.proxy.rlwy.net:PORT -L | head -5

# 3. Topic operations
kcat -b your-kafka.proxy.rlwy.net:PORT -Q -t test-topic
```

---

## 💡 **Best Practices**

### **1. Topic Management**
- Use 1-3 partitions for single node
- Set appropriate retention policies
- Monitor disk usage

### **2. Producer Configuration**
```python
producer_config = {
    'bootstrap.servers': 'your-kafka.proxy.rlwy.net:PORT',
    'acks': 'all',
    'retries': 3,
    'batch.size': 16384,
    'linger.ms': 10
}
```

### **3. Consumer Configuration**
```python
consumer_config = {
    'bootstrap.servers': 'your-kafka.proxy.rlwy.net:PORT',
    'group.id': 'your-consumer-group',
    'auto.offset.reset': 'earliest',
    'session.timeout.ms': 30000
}
```

---

## 🔄 **Upgrade Path**

### **From ZooKeeper to KRaft**
1. Deploy this KRaft template
2. Update client configurations
3. Migrate topics if needed
4. Decommission ZooKeeper cluster

### **Scaling Considerations**
- Single node suitable for development/small production
- Consider Confluent Cloud for high-volume production
- Multiple Railway services for horizontal scaling

---

## 📝 **License**

This template is open source. Use it freely for your Railway Kafka deployments.

---

## 🤝 **Contributing**

1. Fork the repository
2. Create your feature branch
3. Test with local Docker Compose
4. Submit a pull request

---

## 📞 **Support**

- **Railway Issues**: Check Railway status page
- **Kafka Issues**: Refer to Apache Kafka documentation
- **Template Issues**: Open GitHub issue

---

**🎉 Ready to deploy stable, cost-effective Kafka on Railway with KRaft!**