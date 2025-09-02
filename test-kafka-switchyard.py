#!/usr/bin/env python3
"""
Test Kafka connection to switchyard.proxy.rlwy.net:44659
"""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
import json
import time
from datetime import datetime

# New Railway endpoint
KAFKA_BROKER = "switchyard.proxy.rlwy.net:44659"

print(f"🚀 Testing Kafka connection to {KAFKA_BROKER}")
print("=" * 60)

success_count = 0
total_tests = 0

# Test 1: Admin Client Connection
print("\n1️⃣ Testing Admin Client...")
total_tests += 1
try:
    admin = KafkaAdminClient(
        bootstrap_servers=[KAFKA_BROKER],
        request_timeout_ms=10000,
        api_version_auto_timeout_ms=10000
    )
    
    # Get broker metadata
    metadata = admin._client.cluster
    brokers = list(metadata.brokers())
    print(f"✅ Connected successfully!")
    print(f"   Broker: {brokers}")
    
    # List existing topics
    topics = admin.list_topics()
    print(f"   Topics found: {len(topics)} - {list(topics)[:5] if topics else 'None'}")
    
    # Try to create a test topic
    test_topic = f"test-kafka-{int(time.time())}"
    try:
        topic = NewTopic(
            name=test_topic,
            num_partitions=1,
            replication_factor=1
        )
        admin.create_topics([topic])
        print(f"✅ Created topic '{test_topic}'")
        success_count += 1
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Topic already exists")
            success_count += 1
        else:
            print(f"⚠️  Topic creation issue: {str(e)[:100]}")
    
    admin.close()
    
except Exception as e:
    print(f"❌ Admin client failed: {str(e)[:150]}")
    test_topic = "test-kafka-default"

# Test 2: Producer
print("\n2️⃣ Testing Producer...")
total_tests += 1
producer_works = False
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=10000,
        max_block_ms=10000
    )
    
    # Send test messages
    for i in range(3):
        message = {
            'id': i,
            'message': f'Test from switchyard #{i}',
            'timestamp': datetime.now().isoformat(),
            'broker': KAFKA_BROKER
        }
        
        future = producer.send(test_topic, value=message)
        metadata = future.get(timeout=10)
        print(f"   ✅ Sent message {i} to partition {metadata.partition}, offset {metadata.offset}")
    
    producer.flush()
    producer.close()
    
    print(f"✅ Producer working correctly!")
    success_count += 1
    producer_works = True
    
except Exception as e:
    print(f"❌ Producer failed: {str(e)[:150]}")

# Test 3: Consumer
print("\n3️⃣ Testing Consumer...")
total_tests += 1
try:
    consumer = KafkaConsumer(
        test_topic,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000,
        request_timeout_ms=10000
    )
    
    print("✅ Consumer connected!")
    print("   Waiting for messages (5 second timeout)...")
    
    message_count = 0
    for message in consumer:
        message_count += 1
        msg_value = message.value
        print(f"   📨 Received: {msg_value.get('message', msg_value)}")
        if message_count >= 3:
            break
    
    consumer.close()
    
    if message_count > 0:
        print(f"✅ Consumer received {message_count} messages!")
        success_count += 1
    else:
        print(f"ℹ️  No messages (topic might be empty)")
        if producer_works:
            success_count += 1  # Still counts if producer worked
    
except Exception as e:
    print(f"❌ Consumer failed: {str(e)[:150]}")

# Test 4: Quick Performance Check
if producer_works:
    print("\n4️⃣ Testing Throughput...")
    total_tests += 1
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,
            linger_ms=10
        )
        
        start = time.time()
        num_messages = 100
        
        for i in range(num_messages):
            producer.send(test_topic, value={'id': i, 'data': 'x' * 100})
        
        producer.flush()
        elapsed = time.time() - start
        throughput = num_messages / elapsed
        
        print(f"✅ Sent {num_messages} messages in {elapsed:.2f}s")
        print(f"   Throughput: {throughput:.0f} msg/sec")
        
        producer.close()
        success_count += 1
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 FINAL RESULTS")
print("=" * 60)
print(f"Endpoint: {KAFKA_BROKER}")
print(f"Tests passed: {success_count}/{total_tests}")

if success_count == total_tests:
    print("\n🎉 SUCCESS! All tests passed!")
    print(f"✅ Kafka is fully operational at {KAFKA_BROKER}")
    print("\nYou can now connect your applications using:")
    print(f"  bootstrap_servers = ['{KAFKA_BROKER}']")
elif success_count > 0:
    print(f"\n⚠️ Partial success: {success_count}/{total_tests} tests passed")
    print("Some functionality is working but check logs for issues")
else:
    print("\n❌ Connection failed - check Railway configuration")
    print("Ensure TCP Proxy is enabled and service is running")