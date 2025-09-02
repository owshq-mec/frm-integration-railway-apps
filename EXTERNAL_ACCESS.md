# 🌐 Kafka External Access Configuration

This document explains how to configure and connect to Kafka from external clients when deployed on Railway.

## 🚀 Railway TCP Proxy Setup

### 1. Enable TCP Proxy in Railway
1. Go to your Kafka service in Railway dashboard
2. Navigate to Settings → Networking
3. Enable "TCP Proxy"
4. Railway will provide:
   - `RAILWAY_TCP_PROXY_DOMAIN`: Your external domain
   - `RAILWAY_TCP_PROXY_PORT`: Your external port

### 2. Environment Variables Set Automatically

The template configures these variables automatically:

```env
# Core Kafka Configuration
KAFKA_NODE_ID=1
KAFKA_PROCESS_ROLES=broker,controller
KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093

# Listener Configuration for External Access
KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093,EXTERNAL://0.0.0.0:9094
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092,EXTERNAL://${RAILWAY_TCP_PROXY_DOMAIN}:${RAILWAY_TCP_PROXY_PORT}
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT
KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT

# Performance Settings
KAFKA_HEAP_OPTS=-Xmx512m -Xms512m
KAFKA_NUM_PARTITIONS=3
KAFKA_DEFAULT_REPLICATION_FACTOR=1
KAFKA_COMPRESSION_TYPE=snappy
KAFKA_MESSAGE_MAX_BYTES=5242880

# Auto Topic Creation
KAFKA_AUTO_CREATE_TOPICS_ENABLE=true
KAFKA_DELETE_TOPIC_ENABLE=true
```

## 📡 Connecting External Clients

### Python Client Example

```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Get these values from Railway dashboard
KAFKA_BROKER = "your-service.railway.internal:PORT"  # From Railway TCP Proxy

# Producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send message
producer.send('my-topic', {'key': 'value'})
producer.flush()

# Consumer
consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(message.value)
```

### Java Client Example

```java
Properties props = new Properties();
props.put("bootstrap.servers", "your-service.railway.internal:PORT");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("my-topic", "key", "value"));
producer.close();
```

### Node.js Client Example

```javascript
const { Kafka } = require('kafkajs')

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['your-service.railway.internal:PORT']
})

const producer = kafka.producer()
await producer.connect()
await producer.send({
  topic: 'my-topic',
  messages: [
    { value: 'Hello Kafka!' },
  ],
})
```

## 🔧 Troubleshooting

### Connection Issues
1. **Verify TCP Proxy is enabled** in Railway settings
2. **Check firewall rules** if connecting from corporate networks
3. **Ensure correct domain and port** from Railway dashboard

### Common Errors

| Error | Solution |
|-------|----------|
| `Connection refused` | TCP Proxy not enabled or wrong port |
| `Unknown host` | Incorrect domain from Railway |
| `Timeout` | Network firewall blocking connection |
| `Authentication failed` | Check if SASL is required (add auth config) |

## 🔒 Security Considerations

### For Production Use
1. **Enable SASL/SCRAM authentication**:
   ```env
   KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,EXTERNAL:SASL_PLAINTEXT
   KAFKA_SASL_ENABLED_MECHANISMS=SCRAM-SHA-256
   ```

2. **Use SSL/TLS encryption**:
   ```env
   KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,EXTERNAL:SSL
   KAFKA_SSL_KEYSTORE_LOCATION=/path/to/keystore
   KAFKA_SSL_KEYSTORE_PASSWORD=yourpassword
   ```

3. **Implement ACLs** for topic/consumer group authorization

## 📊 Monitoring

### JMX Access
JMX is exposed on port 9999 for monitoring tools like:
- Kafka Manager
- Prometheus JMX Exporter
- JConsole

### Metrics to Monitor
- `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec`
- `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec`
- `kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec`
- `kafka.log:type=LogFlushStats,name=LogFlushRateAndTimeMs`

## 🚦 Health Checks

The service includes automatic health checks:
- **Endpoint**: `kafka-broker-api-versions.sh --bootstrap-server localhost:9092`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start period**: 60 seconds

## 📝 Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_NUM_PARTITIONS` | 3 | Default partitions for new topics |
| `KAFKA_LOG_RETENTION_HOURS` | 168 | How long to keep messages (7 days) |
| `KAFKA_LOG_RETENTION_BYTES` | 1GB | Max size per partition |
| `KAFKA_MESSAGE_MAX_BYTES` | 5MB | Max message size |
| `KAFKA_HEAP_OPTS` | 512MB | JVM heap size |
| `KAFKA_COMPRESSION_TYPE` | snappy | Default compression |

## 🆘 Support

For issues specific to:
- **Kafka configuration**: Check Apache Kafka documentation
- **Railway deployment**: Contact Railway support
- **This template**: Open an issue on GitHub