#!/usr/bin/env python3
"""
Test Kafka connection on port 9093
"""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
import json
import time

KAFKA_BROKER = "centerbeam.proxy.rlwy.net:9093"

print(f"🚀 Testing Kafka connection to {KAFKA_BROKER}")
print("=" * 60)

# Test 1: Admin Client
print("\n1️⃣ Testing Admin Client...")
try:
    admin = KafkaAdminClient(
        bootstrap_servers=[KAFKA_BROKER],
        request_timeout_ms=10000
    )
    
    # List topics
    topics = admin.list_topics()
    print(f"✅ Connected successfully!")
    print(f"   Existing topics: {topics if topics else '(no topics yet)'}")
    
    # Try to create a test topic
    try:
        topic = NewTopic(name="test-topic", num_partitions=1, replication_factor=1)
        admin.create_topics([topic])
        print(f"✅ Created topic 'test-topic'")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Topic 'test-topic' already exists")
        else:
            print(f"⚠️  Could not create topic: {e}")
    
    admin.close()
    
except Exception as e:
    print(f"❌ Admin client failed: {e}")

# Test 2: Producer
print("\n2️⃣ Testing Producer...")
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=10000
    )
    
    # Send a test message
    message = {
        'test': 'Hello from Railway Kafka!',
        'timestamp': time.time(),
        'port': 9093
    }
    
    future = producer.send('test-topic', value=message)
    metadata = future.get(timeout=10)
    
    print(f"✅ Message sent successfully!")
    print(f"   Topic: {metadata.topic}")
    print(f"   Partition: {metadata.partition}")
    print(f"   Offset: {metadata.offset}")
    
    producer.close()
    
except Exception as e:
    print(f"❌ Producer failed: {e}")

# Test 3: Consumer
print("\n3️⃣ Testing Consumer...")
try:
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000
    )
    
    print("✅ Consumer connected successfully!")
    print("   Waiting for messages (5 second timeout)...")
    
    message_count = 0
    for message in consumer:
        message_count += 1
        print(f"   📨 Received: {message.value}")
        if message_count >= 3:
            break
    
    if message_count == 0:
        print("   ℹ️ No messages received (topic might be empty)")
    else:
        print(f"   ✅ Received {message_count} message(s)")
    
    consumer.close()
    
except Exception as e:
    print(f"❌ Consumer failed: {e}")

print("\n" + "=" * 60)
print("📊 CONNECTION SUMMARY")
print("=" * 60)
print(f"Broker: {KAFKA_BROKER}")
print("\nIf all tests passed, your Kafka is working correctly!")
print("External clients can connect using this broker address.")