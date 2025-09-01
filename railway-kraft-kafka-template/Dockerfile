FROM confluentinc/cp-kafka:7.5.0

# Set environment variables for KRaft mode
ENV KAFKA_PROCESS_ROLES=broker,controller
ENV KAFKA_NODE_ID=1
ENV KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093
ENV KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
ENV KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT
ENV KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER
ENV KAFKA_LOG_DIRS=/var/lib/kafka/data
ENV KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
ENV KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1
ENV KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1
ENV KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS=0

# External access configuration (will be overridden by Railway variables)
ENV KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092

# Memory and performance optimization for Railway
ENV KAFKA_HEAP_OPTS="-Xmx512m -Xms512m"
ENV KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35"

# Retention and performance settings optimized for Railway
ENV KAFKA_LOG_RETENTION_HOURS=168
ENV KAFKA_LOG_RETENTION_BYTES=1073741824
ENV KAFKA_LOG_SEGMENT_BYTES=1073741824
ENV KAFKA_NUM_PARTITIONS=3
ENV KAFKA_DEFAULT_REPLICATION_FACTOR=1
ENV KAFKA_MIN_INSYNC_REPLICAS=1

# JMX monitoring
ENV KAFKA_JMX_PORT=9999
ENV KAFKA_JMX_HOSTNAME=localhost

# Copy startup script first and set permissions as root
COPY --chmod=755 start-kraft-kafka.sh /usr/local/bin/

# Create data directory and set permissions
RUN mkdir -p /var/lib/kafka/data && \
    chown -R appuser:appuser /var/lib/kafka/data

# Expose ports
EXPOSE 9092 9093 9999

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD kafka-broker-api-versions --bootstrap-server localhost:9092 || exit 1

# Switch to appuser for security
USER appuser

CMD ["/usr/local/bin/start-kraft-kafka.sh"]