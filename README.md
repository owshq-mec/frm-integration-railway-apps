# 🚄 Railway Integration Apps Collection

Collection of production-ready Railway templates and integrations for data engineering and streaming applications.

## 📦 **Available Templates**

### 🚀 **KRaft Kafka Template**
**Location**: `railway-kraft-kafka-template/`

Production-ready Apache Kafka using **KRaft mode** (no ZooKeeper) optimized for Railway platform.

**Features:**
- ✅ **No ZooKeeper dependency** - eliminates session instability
- ✅ **External TCP access** pre-configured
- ✅ **Production optimized** memory and performance settings
- ✅ **90% cost savings** vs managed Kafka services
- ✅ **One-click deployment** ready

**Deploy:**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

```bash
cd railway-kraft-kafka-template/
railway up
# Enable TCP Proxy in Railway dashboard
```

**External Access:**
```bash
# Your Kafka endpoint after deployment
your-service.proxy.rlwy.net:PORT

# Test connectivity
kcat -b your-service.proxy.rlwy.net:PORT -L
```

---

## 🎯 **Use Cases**

- **UberEats Data Streaming**: Real-time order and delivery event processing
- **IoT Data Ingestion**: High-throughput sensor data collection
- **Microservices Communication**: Event-driven architecture messaging
- **Development & Testing**: Cost-effective Kafka for non-production workloads

---

## 🏗️ **Architecture Benefits**

| Component | Traditional Setup | Railway KRaft | Savings |
|-----------|-------------------|---------------|---------|
| **Services** | Kafka + ZooKeeper | Kafka Only | 50% less complexity |
| **Memory Usage** | 1GB+ | 512MB | 50% reduction |
| **Monthly Cost** | $100-300 | $10-20 | 90% savings |
| **Stability** | Session dependencies | Self-contained | Zero session issues |

---

## 📚 **Documentation**

Each template includes:
- Complete setup and deployment guides
- Local development with Docker Compose  
- Production configuration examples
- Testing and validation scripts
- Troubleshooting guides

---

**Status**: 🎉 **Ready for production deployment on Railway**