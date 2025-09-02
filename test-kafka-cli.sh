#!/bin/bash

KAFKA_BROKER="centerbeam.proxy.rlwy.net:35405"
TOPIC="test-railway"

echo "🚀 Testing Kafka connection using official CLI tools"
echo "=================================================="
echo "Broker: $KAFKA_BROKER"
echo ""

# Test 1: List topics
echo "1️⃣ Listing topics..."
docker run --rm apache/kafka:latest \
    /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server $KAFKA_BROKER \
    --list \
    --command-config /dev/null 2>&1

echo ""

# Test 2: Create a topic
echo "2️⃣ Creating test topic '$TOPIC'..."
docker run --rm apache/kafka:latest \
    /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server $KAFKA_BROKER \
    --create \
    --topic $TOPIC \
    --partitions 3 \
    --replication-factor 1 \
    --if-not-exists 2>&1

echo ""

# Test 3: Describe the topic
echo "3️⃣ Describing topic '$TOPIC'..."
docker run --rm apache/kafka:latest \
    /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server $KAFKA_BROKER \
    --describe \
    --topic $TOPIC 2>&1

echo ""

# Test 4: Produce a test message
echo "4️⃣ Sending test message..."
echo "Hello Railway Kafka $(date)" | docker run -i --rm apache/kafka:latest \
    /opt/kafka/bin/kafka-console-producer.sh \
    --bootstrap-server $KAFKA_BROKER \
    --topic $TOPIC 2>&1

echo ""

# Test 5: Consume messages
echo "5️⃣ Consuming messages (5 second timeout)..."
docker run --rm apache/kafka:latest \
    timeout 5 /opt/kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server $KAFKA_BROKER \
    --topic $TOPIC \
    --from-beginning \
    --max-messages 5 2>&1

echo ""
echo "=================================================="
echo "✅ Test complete!"
echo ""
echo "If you see errors above, check:"
echo "1. Railway TCP Proxy is enabled"
echo "2. The service is running"
echo "3. The domain and port are correct"