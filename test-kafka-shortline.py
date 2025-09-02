#!/usr/bin/env python3
"""
Test Kafka connection to shortline.proxy.rlwy.net
"""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
import json
import time

# Railway TCP Proxy endpoint
KAFKA_BROKER = "shortline.proxy.rlwy.net:35405"

print(f"🚀 Testing NEW Kafka connection to {KAFKA_BROKER}")
print("=" * 60)

# Test 1: Admin Client
print("\n1️⃣ Testing Admin Client...")
try:
    admin = KafkaAdminClient(
        bootstrap_servers=[KAFKA_BROKER],
        request_timeout_ms=10000,
        api_version_auto_timeout_ms=10000
    )
    
    # Get metadata
    metadata = admin._client.cluster
    print(f"✅ Connected successfully!")
    print(f"   Broker ID: {list(metadata.brokers())}")
    
    # List topics
    topics = admin.list_topics()
    print(f"   Existing topics: {topics if topics else '(no topics yet)'}")
    
    # Try to create a test topic
    try:
        topic = NewTopic(
            name="railway-test", 
            num_partitions=3, 
            replication_factor=1
        )
        result = admin.create_topics([topic])
        print(f"✅ Created topic 'railway-test' with 3 partitions")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Topic 'railway-test' already exists")
        else:
            print(f"⚠️  Could not create topic: {str(e)[:100]}")
    
    admin.close()
    admin_success = True
    
except Exception as e:
    print(f"❌ Admin client failed: {str(e)[:200]}")
    admin_success = False

# Test 2: Producer
print("\n2️⃣ Testing Producer...")
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=10000,
        max_block_ms=10000
    )
    
    # Send test messages
    messages_sent = 0
    for i in range(3):
        message = {
            'id': i,
            'message': f'Test message {i}',
            'timestamp': time.time(),
            'broker': KAFKA_BROKER
        }
        
        future = producer.send('railway-test', value=message)
        metadata = future.get(timeout=10)
        messages_sent += 1
        
        print(f"   ✅ Message {i} sent to partition {metadata.partition} at offset {metadata.offset}")
    
    producer.flush()
    producer.close()
    
    print(f"✅ Successfully sent {messages_sent} messages")
    producer_success = True
    
except Exception as e:
    print(f"❌ Producer failed: {str(e)[:200]}")
    producer_success = False

# Test 3: Consumer
print("\n3️⃣ Testing Consumer...")
try:
    consumer = KafkaConsumer(
        'railway-test',
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000,
        request_timeout_ms=10000
    )
    
    print("✅ Consumer connected successfully!")
    print("   Reading messages (5 second timeout)...")
    
    messages_received = 0
    for message in consumer:
        messages_received += 1
        print(f"   📨 Message: {message.value}")
        if messages_received >= 3:
            break
    
    consumer.close()
    
    if messages_received > 0:
        print(f"✅ Received {messages_received} message(s)")
        consumer_success = True
    else:
        print("ℹ️  No messages received (topic might be empty)")
        consumer_success = True  # Still counts as success if connected
    
except Exception as e:
    print(f"❌ Consumer failed: {str(e)[:200]}")
    consumer_success = False

# Test 4: Performance test
if producer_success:
    print("\n4️⃣ Testing Performance...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,
            linger_ms=10
        )
        
        start_time = time.time()
        messages_to_send = 50
        
        for i in range(messages_to_send):
            message = {'id': i, 'data': 'x' * 100}
            producer.send('railway-test', value=message)
        
        producer.flush()
        elapsed = time.time() - start_time
        throughput = messages_to_send / elapsed
        
        print(f"✅ Sent {messages_to_send} messages in {elapsed:.2f}s")
        print(f"   Throughput: {throughput:.1f} messages/second")
        
        producer.close()
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print(f"Broker: {KAFKA_BROKER}")
print(f"Admin Client: {'✅ PASSED' if admin_success else '❌ FAILED'}")
print(f"Producer: {'✅ PASSED' if producer_success else '❌ FAILED'}")
print(f"Consumer: {'✅ PASSED' if consumer_success else '❌ FAILED'}")

if admin_success and producer_success and consumer_success:
    print("\n🎉 SUCCESS! Kafka is working correctly!")
    print(f"✅ External clients can connect to: {KAFKA_BROKER}")
else:
    print("\n⚠️ Some tests failed. Check Railway configuration.")
    print("Make sure TCP Proxy 'Application Port' is set to 9094")