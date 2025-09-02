#!/bin/bash
set -e

echo "🚀 Starting Kafka in KRaft Mode"
echo "================================"
echo "Node ID: $KAFKA_NODE_ID"
echo "Process Roles: $KAFKA_PROCESS_ROLES"

# Generate cluster UUID if not provided
if [ -z "$KAFKA_CLUSTER_ID" ]; then
    export KAFKA_CLUSTER_ID=$(/opt/kafka/bin/kafka-storage.sh random-uuid)
    echo "Generated Cluster ID: $KAFKA_CLUSTER_ID"
else
    echo "Using provided Cluster ID: $KAFKA_CLUSTER_ID"
fi

# Configure external access using Railway TCP proxy
if [ -n "$RAILWAY_TCP_PROXY_DOMAIN" ] && [ -n "$RAILWAY_TCP_PROXY_PORT" ]; then
    export KAFKA_LISTENERS="${KAFKA_LISTENERS:-PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093,EXTERNAL://0.0.0.0:9094}"
    export KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://localhost:9092,EXTERNAL://$RAILWAY_TCP_PROXY_DOMAIN:$RAILWAY_TCP_PROXY_PORT"
    export KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="${KAFKA_LISTENER_SECURITY_PROTOCOL_MAP:-PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT}"
    echo "TCP Proxy configured for external access:"
    echo "  External endpoint: $RAILWAY_TCP_PROXY_DOMAIN:$RAILWAY_TCP_PROXY_PORT"
    echo "  Listeners: $KAFKA_LISTENERS"
elif [ -n "$RAILWAY_PUBLIC_DOMAIN" ] && [ -n "$PORT" ]; then
    export KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://$RAILWAY_PUBLIC_DOMAIN:$PORT"
    echo "Public domain configured: $RAILWAY_PUBLIC_DOMAIN:$PORT"
else
    export KAFKA_LISTENERS="${KAFKA_LISTENERS:-PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093}"
    export KAFKA_ADVERTISED_LISTENERS="${KAFKA_ADVERTISED_LISTENERS:-PLAINTEXT://localhost:9092}"
    echo "Using localhost configuration (local development)"
fi

# Update controller quorum voters if running in cluster mode
if [ -n "$KAFKA_CONTROLLER_QUORUM_VOTERS_OVERRIDE" ]; then
    export KAFKA_CONTROLLER_QUORUM_VOTERS="$KAFKA_CONTROLLER_QUORUM_VOTERS_OVERRIDE"
    echo "Controller quorum voters: $KAFKA_CONTROLLER_QUORUM_VOTERS"
fi

# Create Kafka properties file for KRaft
cat > /tmp/server.properties << EOF
# KRaft Configuration
process.roles=$KAFKA_PROCESS_ROLES
node.id=$KAFKA_NODE_ID
controller.quorum.voters=$KAFKA_CONTROLLER_QUORUM_VOTERS

# Listeners
listeners=$KAFKA_LISTENERS
advertised.listeners=$KAFKA_ADVERTISED_LISTENERS
listener.security.protocol.map=${KAFKA_LISTENER_SECURITY_PROTOCOL_MAP:-PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT}
inter.broker.listener.name=$KAFKA_INTER_BROKER_LISTENER_NAME
controller.listener.names=$KAFKA_CONTROLLER_LISTENER_NAMES

# Log directories
log.dirs=$KAFKA_LOG_DIRS

# Replication settings
offsets.topic.replication.factor=$KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
transaction.state.log.replication.factor=$KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR
transaction.state.log.min.isr=$KAFKA_TRANSACTION_STATE_LOG_MIN_ISR

# Topic defaults
num.partitions=$KAFKA_NUM_PARTITIONS
default.replication.factor=$KAFKA_DEFAULT_REPLICATION_FACTOR
min.insync.replicas=$KAFKA_MIN_INSYNC_REPLICAS

# Performance optimization
group.initial.rebalance.delay.ms=$KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS
log.retention.hours=$KAFKA_LOG_RETENTION_HOURS
log.retention.bytes=$KAFKA_LOG_RETENTION_BYTES
log.segment.bytes=$KAFKA_LOG_SEGMENT_BYTES
log.cleanup.policy=${KAFKA_LOG_CLEANUP_POLICY:-delete}

# Auto topic creation
auto.create.topics.enable=${KAFKA_AUTO_CREATE_TOPICS_ENABLE:-true}
delete.topic.enable=${KAFKA_DELETE_TOPIC_ENABLE:-true}

# Compression and message size
compression.type=${KAFKA_COMPRESSION_TYPE:-snappy}
message.max.bytes=${KAFKA_MESSAGE_MAX_BYTES:-5242880}
replica.fetch.max.bytes=${KAFKA_REPLICA_FETCH_MAX_BYTES:-5242880}
max.request.size=${KAFKA_MAX_REQUEST_SIZE:-5242880}

# Network and request handling
num.network.threads=${KAFKA_NUM_NETWORK_THREADS:-8}
num.io.threads=${KAFKA_NUM_IO_THREADS:-8}
socket.send.buffer.bytes=${KAFKA_SOCKET_SEND_BUFFER_BYTES:-102400}
socket.receive.buffer.bytes=${KAFKA_SOCKET_RECEIVE_BUFFER_BYTES:-102400}
socket.request.max.bytes=${KAFKA_SOCKET_REQUEST_MAX_BYTES:-104857600}

# JMX monitoring
jmx.port=$KAFKA_JMX_PORT
EOF

# Check if storage is already formatted
if [ ! -f "$KAFKA_LOG_DIRS/meta.properties" ]; then
    echo "📦 Formatting Kafka storage (first run)..."
    /opt/kafka/bin/kafka-storage.sh format \
        --config /tmp/server.properties \
        --cluster-id $KAFKA_CLUSTER_ID \
        --ignore-formatted
    echo "✅ Storage formatted successfully"
else
    echo "📦 Using existing formatted storage"
fi

# Verify configuration
echo "🔍 Configuration Summary:"
echo "  Advertised Listeners: $KAFKA_ADVERTISED_LISTENERS"
echo "  Log Dirs: $KAFKA_LOG_DIRS"
echo "  Cluster ID: $KAFKA_CLUSTER_ID"
echo "  Memory: $KAFKA_HEAP_OPTS"

# Start Kafka server
echo "🎯 Starting Kafka KRaft server..."
echo "================================"

exec /opt/kafka/bin/kafka-server-start.sh /tmp/server.properties