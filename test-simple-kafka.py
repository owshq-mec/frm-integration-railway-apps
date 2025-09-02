#!/usr/bin/env python3
"""
Simple Kafka Connection Test - Auto-detects API version
"""

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import time

KAFKA_BROKER = "centerbeam.proxy.rlwy.net:35405"

print(f"🔍 Testing connection to Kafka at {KAFKA_BROKER}")
print("=" * 60)

# Test 1: Try producer with auto API version detection
print("\n1️⃣ Testing Producer with auto API version...")
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        api_version=(3, 5, 0),  # Apache Kafka 3.5.0
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=30000,
        max_block_ms=30000
    )
    
    # Try to send a test message
    message = {
        'test': 'Hello Railway Kafka!',
        'timestamp': time.time()
    }
    
    future = producer.send('test-topic', value=message)
    result = future.get(timeout=10)
    
    print(f"✅ Producer connected successfully!")
    print(f"   Message sent to partition {result.partition} at offset {result.offset}")
    
    producer.close()
    
except NoBrokersAvailable as e:
    print(f"❌ No brokers available: {e}")
    print("   The broker might not be reachable or TCP proxy is not configured")
except Exception as e:
    print(f"❌ Producer failed: {type(e).__name__}: {e}")

# Test 2: Try consumer
print("\n2️⃣ Testing Consumer...")
try:
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers=[KAFKA_BROKER],
        api_version=(3, 5, 0),  # Apache Kafka 3.5.0
        auto_offset_reset='latest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000
    )
    
    print("✅ Consumer connected successfully!")
    print("   Waiting for messages (5 second timeout)...")
    
    message_count = 0
    for message in consumer:
        message_count += 1
        print(f"   Received: {message.value}")
        if message_count >= 3:
            break
    
    if message_count == 0:
        print("   No messages received (topic might be empty)")
    
    consumer.close()
    
except Exception as e:
    print(f"❌ Consumer failed: {type(e).__name__}: {e}")

# Test 3: Try without specifying API version (auto-detect)
print("\n3️⃣ Testing with API version auto-detection...")
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: v.encode('utf-8'),
        request_timeout_ms=30000
    )
    
    # Get broker metadata
    metadata = producer._metadata
    
    if metadata.brokers():
        print(f"✅ Connected with auto-detection!")
        print(f"   Brokers: {list(metadata.brokers())}")
        print(f"   Topics: {metadata.topics()}")
    
    producer.close()
    
except Exception as e:
    print(f"❌ Auto-detection failed: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("📝 Connection Summary:")
print(f"   Broker: {KAFKA_BROKER}")
print("\n💡 If connection fails:")
print("   1. Check Railway logs for the Kafka service")
print("   2. Verify TCP Proxy is enabled and showing the domain")
print("   3. Ensure the service is running (not crashed)")
print("   4. Try using port 9092 if 35405 doesn't work")