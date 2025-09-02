#!/usr/bin/env python3
"""
Kafka Connection Test Script for Railway Deployment
Tests connection to Kafka instance at centerbeam.proxy.rlwy.net:35405
"""

import json
import time
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError
import sys

# Kafka connection details from Railway TCP Proxy
KAFKA_BROKER = "centerbeam.proxy.rlwy.net:35405"  # Using Railway TCP Proxy port
TEST_TOPIC = "test-railway-kafka"

def test_admin_connection():
    """Test admin client connection and topic creation"""
    print(f"\n🔍 Testing Admin Connection to {KAFKA_BROKER}...")
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=KAFKA_BROKER,
            request_timeout_ms=10000,
            api_version_auto_timeout_ms=10000
        )
        
        # Get cluster metadata
        metadata = admin._client.cluster
        print(f"✅ Connected to Kafka cluster")
        print(f"   Broker: {metadata.brokers()}")
        
        # List existing topics
        topics = admin.list_topics()
        print(f"   Existing topics: {topics}")
        
        # Try to create a test topic
        topic = NewTopic(
            name=TEST_TOPIC,
            num_partitions=3,
            replication_factor=1
        )
        
        try:
            result = admin.create_topics([topic])
            print(f"✅ Created topic '{TEST_TOPIC}' with 3 partitions")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Topic '{TEST_TOPIC}' already exists")
            else:
                print(f"⚠️  Could not create topic: {e}")
        
        admin.close()
        return True
        
    except Exception as e:
        print(f"❌ Admin connection failed: {e}")
        return False

def test_producer():
    """Test producing messages to Kafka"""
    print(f"\n📤 Testing Producer Connection...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=10000,
            api_version_auto_timeout_ms=10000
        )
        
        # Send test messages
        messages_sent = 0
        for i in range(5):
            message = {
                'id': i,
                'timestamp': datetime.now().isoformat(),
                'message': f'Test message {i} from Railway Kafka',
                'source': 'test-script'
            }
            
            future = producer.send(TEST_TOPIC, value=message)
            record_metadata = future.get(timeout=10)
            messages_sent += 1
            
            print(f"   ✅ Sent message {i} to partition {record_metadata.partition} at offset {record_metadata.offset}")
        
        producer.flush()
        producer.close()
        
        print(f"✅ Successfully sent {messages_sent} messages")
        return True
        
    except KafkaError as e:
        print(f"❌ Producer error: {e}")
        return False
    except Exception as e:
        print(f"❌ Producer connection failed: {e}")
        return False

def test_consumer():
    """Test consuming messages from Kafka"""
    print(f"\n📥 Testing Consumer Connection...")
    try:
        consumer = KafkaConsumer(
            TEST_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=5000,  # Stop after 5 seconds of no messages
            api_version_auto_timeout_ms=10000
        )
        
        print(f"   Consuming messages from '{TEST_TOPIC}'...")
        messages_received = 0
        
        for message in consumer:
            messages_received += 1
            print(f"   ✅ Received: {message.value}")
            
            if messages_received >= 5:  # Read up to 5 messages
                break
        
        consumer.close()
        
        if messages_received > 0:
            print(f"✅ Successfully consumed {messages_received} messages")
            return True
        else:
            print(f"⚠️  No messages received (topic might be empty)")
            return True  # Still consider it a success if connection worked
        
    except Exception as e:
        print(f"❌ Consumer connection failed: {e}")
        return False

def test_performance():
    """Test basic performance metrics"""
    print(f"\n⚡ Testing Performance...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,
            linger_ms=10
        )
        
        start_time = time.time()
        messages_to_send = 100
        
        for i in range(messages_to_send):
            message = {
                'id': i,
                'data': 'x' * 1000  # 1KB message
            }
            producer.send(TEST_TOPIC, value=message)
        
        producer.flush()
        elapsed_time = time.time() - start_time
        
        throughput = messages_to_send / elapsed_time
        print(f"✅ Sent {messages_to_send} messages in {elapsed_time:.2f} seconds")
        print(f"   Throughput: {throughput:.2f} messages/second")
        
        producer.close()
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("=" * 60)
    print("🚀 KAFKA RAILWAY CONNECTION TEST")
    print(f"   Target: {KAFKA_BROKER}")
    print(f"   Topic: {TEST_TOPIC}")
    print("=" * 60)
    
    # Track test results
    results = {
        'admin': False,
        'producer': False,
        'consumer': False,
        'performance': False
    }
    
    # Run tests
    results['admin'] = test_admin_connection()
    
    if results['admin']:
        results['producer'] = test_producer()
        
        if results['producer']:
            time.sleep(2)  # Give messages time to be committed
            results['consumer'] = test_consumer()
            results['performance'] = test_performance()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name.capitalize()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Kafka is working correctly on Railway.")
        print(f"   External clients can connect to: {KAFKA_BROKER}")
    else:
        print("\n⚠️  Some tests failed. Check the configuration and logs.")
        print("\nTroubleshooting:")
        print("1. Verify TCP Proxy is enabled in Railway")
        print("2. Check if the domain/port are correct")
        print("3. Ensure Kafka container is running")
        print("4. Check Railway logs for errors")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        # Install required package if not present
        import kafka
    except ImportError:
        print("Installing kafka-python package...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kafka-python"])
        print("Package installed. Please run the script again.")
        sys.exit(1)
    
    sys.exit(main())