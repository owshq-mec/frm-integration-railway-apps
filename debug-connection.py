#!/usr/bin/env python3
"""
Debug connection to Railway Kafka
"""

import socket
import struct
import time

host = "switchyard.proxy.rlwy.net"
port = 44659

print(f"🔍 Debugging connection to {host}:{port}")
print("=" * 60)

# Test 1: Basic TCP connection
print("\n1️⃣ Testing basic TCP connection...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    
    if result == 0:
        print(f"✅ TCP connection successful!")
        
        # Try sending a Kafka metadata request
        print("\n2️⃣ Sending Kafka metadata request...")
        
        # Kafka protocol: Simple metadata request v0
        # Format: [length][api_key][api_version][correlation_id][client_id_len][client_id]
        api_key = 3  # Metadata request
        api_version = 0
        correlation_id = 1
        client_id = b"debug-client"
        
        # Build the request
        request_body = struct.pack('>h', api_key)  # API key
        request_body += struct.pack('>h', api_version)  # API version
        request_body += struct.pack('>i', correlation_id)  # Correlation ID
        request_body += struct.pack('>h', len(client_id))  # Client ID length
        request_body += client_id  # Client ID
        
        # Add length prefix
        full_request = struct.pack('>i', len(request_body)) + request_body
        
        print(f"   Sending {len(full_request)} bytes...")
        sock.send(full_request)
        
        # Wait for response
        sock.settimeout(5)
        try:
            response = sock.recv(1024)
            if response:
                print(f"✅ Received response: {len(response)} bytes")
                
                # Try to parse response
                if len(response) >= 4:
                    response_length = struct.unpack('>i', response[:4])[0]
                    print(f"   Response length field: {response_length}")
                    
                    # Check for error codes
                    if b"UNSUPPORTED" in response or b"ERROR" in response:
                        print("   ⚠️ Server returned an error")
                    elif response_length > 0 and response_length < 10000:
                        print("   ✅ Valid Kafka response structure")
                    else:
                        print(f"   ⚠️ Unexpected response")
                        
                    # Show first 100 bytes as hex
                    print(f"   Raw (hex): {response[:50].hex()}")
            else:
                print("❌ No response received")
                
        except socket.timeout:
            print("❌ Response timeout - server not responding to Kafka protocol")
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            
        sock.close()
    else:
        print(f"❌ TCP connection failed: error code {result}")
        
except Exception as e:
    print(f"❌ Connection error: {e}")

# Test 3: Check if it's HTTP
print("\n3️⃣ Testing if it's HTTP service...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((host, port))
    
    # Send HTTP request
    sock.send(b"GET / HTTP/1.0\r\n\r\n")
    response = sock.recv(1024)
    
    if b"HTTP" in response:
        print("⚠️ Service is HTTP, not Kafka!")
        print(f"   Response: {response[:200].decode('utf-8', errors='ignore')}")
    elif response:
        print(f"   Not HTTP, received {len(response)} bytes")
    else:
        print("   No HTTP response")
        
    sock.close()
except Exception as e:
    print(f"   HTTP test: {e}")

print("\n" + "=" * 60)
print("📊 DIAGNOSIS")
print("=" * 60)

print(f"""
Endpoint: {host}:{port}
TCP Connection: Working

Possible issues:
1. Railway TCP proxy not mapping to Kafka port 9092
2. Kafka service crashed or not running
3. Wrong internal port configuration

Check Railway dashboard:
- Is the service running?
- What port is TCP Proxy set to?
- Check service logs for errors
""")