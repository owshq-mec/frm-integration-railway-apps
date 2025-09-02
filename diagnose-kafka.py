#!/usr/bin/env python3
"""
Kafka Railway Diagnostic Script
"""

import socket
import struct
import time
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.protocol.api import Request, Response
from kafka.protocol.metadata import MetadataRequest_v0
import sys

KAFKA_BROKER = "centerbeam.proxy.rlwy.net"
KAFKA_PORT = 35405

print("🔍 KAFKA RAILWAY DIAGNOSTIC")
print("=" * 60)

# Test 1: Raw socket connection
print("\n1️⃣ Testing raw TCP connection...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((KAFKA_BROKER, KAFKA_PORT))
    if result == 0:
        print(f"✅ TCP connection successful to {KAFKA_BROKER}:{KAFKA_PORT}")
        
        # Try to send a Kafka API version request
        print("   Attempting to send Kafka protocol handshake...")
        
        # Send a simple metadata request (Kafka protocol)
        # This is a simplified version - real implementation is more complex
        try:
            # Kafka wire protocol: [length][api_key][api_version][correlation_id][client_id_length][client_id]
            api_key = 3  # Metadata
            api_version = 0
            correlation_id = 1
            client_id = b"diagnostic"
            
            # Build request (simplified)
            request = struct.pack('>hhih', api_key, api_version, correlation_id, len(client_id)) + client_id
            length = struct.pack('>i', len(request))
            
            sock.send(length + request)
            
            # Try to receive response
            response = sock.recv(1024)
            if response:
                print(f"   ✅ Received response from Kafka broker ({len(response)} bytes)")
                # Check if it's an error response
                if b"METADATA" in response or b"ERROR" in response:
                    print(f"   Response snippet: {response[:100]}")
            else:
                print("   ⚠️ No response received")
                
        except Exception as e:
            print(f"   ⚠️ Protocol test failed: {e}")
        
        sock.close()
    else:
        print(f"❌ TCP connection failed with error code: {result}")
except Exception as e:
    print(f"❌ Connection error: {e}")

# Test 2: Check what service is responding
print("\n2️⃣ Checking service type...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((KAFKA_BROKER, KAFKA_PORT))
    
    # Send HTTP request to see if it's HTTP service
    sock.send(b"GET / HTTP/1.0\r\n\r\n")
    response = sock.recv(1024)
    
    if b"HTTP" in response:
        print("⚠️ Service is responding with HTTP - might be wrong port")
        print(f"   Response: {response[:200].decode('utf-8', errors='ignore')}")
    elif b"kafka" in response.lower() or len(response) > 0:
        print("✅ Service appears to be Kafka or binary protocol")
        print(f"   Response length: {len(response)} bytes")
    else:
        print("⚠️ Unknown service type")
    
    sock.close()
except Exception as e:
    print(f"   Service check: {e}")

# Test 3: Try different API versions
print("\n3️⃣ Testing Kafka client with different configurations...")

configs_to_test = [
    {"name": "Default", "config": {}},
    {"name": "API v3.5.0", "config": {"api_version": (3, 5, 0)}},
    {"name": "API v2.8.0", "config": {"api_version": (2, 8, 0)}},
    {"name": "Security PLAINTEXT", "config": {"security_protocol": "PLAINTEXT"}},
]

for test_config in configs_to_test:
    print(f"\n   Testing {test_config['name']}...")
    try:
        config = {
            "bootstrap_servers": [f"{KAFKA_BROKER}:{KAFKA_PORT}"],
            "request_timeout_ms": 5000,
            "connections_max_idle_ms": 5000,
            **test_config['config']
        }
        
        admin = KafkaAdminClient(**config)
        
        # Try to get metadata
        topics = admin.list_topics()
        print(f"   ✅ Connected with {test_config['name']}")
        print(f"      Topics: {topics if topics else 'No topics found'}")
        
        admin.close()
        break
        
    except Exception as e:
        error_msg = str(e)
        if "UnsupportedVersion" in error_msg:
            print(f"   ❌ Version mismatch: {error_msg[:100]}")
        elif "NoBrokersAvailable" in error_msg:
            print(f"   ❌ No brokers available")
        elif "KafkaTimeoutError" in error_msg:
            print(f"   ❌ Timeout - broker not responding correctly")
        else:
            print(f"   ❌ Failed: {error_msg[:100]}")

# Test 4: Port scan to find correct port
print("\n4️⃣ Checking if Railway TCP proxy is mapping to correct internal port...")
print("   The TCP proxy might be connecting to wrong internal port.")
print("   Current mapping: External 35405 -> Internal ???")
print("\n   You should check Railway settings:")
print("   1. Go to Railway dashboard")
print("   2. Click on your Kafka service")  
print("   3. Go to Settings → Networking")
print("   4. Under TCP Proxy, check 'TCP Application Port'")
print("   5. It should be set to 9094 (EXTERNAL listener)")
print("      or 9092 (PLAINTEXT listener)")

print("\n" + "=" * 60)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 60)

print(f"""
Connection: {KAFKA_BROKER}:{KAFKA_PORT}
Status: TCP connection works, but Kafka protocol fails

Likely issue: Railway TCP proxy is connected to wrong internal port
- It might be connecting to port 9093 (controller) instead of 9092/9094 (broker)

Solution:
1. In Railway dashboard, set RAILWAY_TCP_APPLICATION_PORT = 9094
2. Or in your railway.json, ensure this is set correctly
3. Redeploy the service

The error "The node does not support METADATA" typically means:
- You're connecting to the controller port (9093) instead of broker port
- The EXTERNAL listener (9094) is not properly configured
""")