#!/bin/bash

# Railway KRaft Kafka Test Script
# Usage: ./test-kraft-kafka.sh [KAFKA_BOOTSTRAP_SERVERS]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default to local if no server provided
KAFKA_SERVERS=${1:-"localhost:9092"}
TEST_TOPIC="kraft-test-topic"

echo -e "${BLUE}🧪 Railway KRaft Kafka Test${NC}"
echo "=============================="
echo -e "Server: ${YELLOW}$KAFKA_SERVERS${NC}"
echo -e "Topic: ${YELLOW}$TEST_TOPIC${NC}"
echo ""

# Function to run test with error handling
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo -e "${BLUE}Testing: $test_name${NC}"
    if eval "$command" 2>/dev/null; then
        echo -e "${GREEN}✅ $test_name: PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name: FAILED${NC}"
        return 1
    fi
    echo ""
}

# Test 1: Basic connectivity
run_test "Basic Connectivity" \
    "kcat -b $KAFKA_SERVERS -L | head -3"

# Test 2: Create and send messages
echo -e "${BLUE}Testing: Message Production${NC}"
SENT_COUNT=0
for i in {1..5}; do
    MESSAGE="{\"test_id\":$i,\"message\":\"KRaft test message $i\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
    if echo "$MESSAGE" | kcat -b "$KAFKA_SERVERS" -t "$TEST_TOPIC" -P 2>/dev/null; then
        ((SENT_COUNT++))
    fi
done

if [ $SENT_COUNT -eq 5 ]; then
    echo -e "${GREEN}✅ Message Production: PASSED (5/5 sent)${NC}"
else
    echo -e "${RED}❌ Message Production: FAILED ($SENT_COUNT/5 sent)${NC}"
fi
echo ""

# Wait a moment for messages to be committed
sleep 2

# Test 3: Message consumption
echo -e "${BLUE}Testing: Message Consumption${NC}"
RECEIVED_COUNT=$(kcat -b "$KAFKA_SERVERS" -t "$TEST_TOPIC" -C -o beginning -e 2>/dev/null | wc -l | xargs)

if [ "$RECEIVED_COUNT" -eq 5 ]; then
    echo -e "${GREEN}✅ Message Consumption: PASSED (5/5 received)${NC}"
else
    echo -e "${YELLOW}⚠️  Message Consumption: PARTIAL ($RECEIVED_COUNT/5 received)${NC}"
fi
echo ""

# Test 4: Topic information
run_test "Topic Metadata" \
    "kcat -b $KAFKA_SERVERS -L -t $TEST_TOPIC"

# Test 5: Latest messages preview
echo -e "${BLUE}Latest Messages Preview:${NC}"
echo "------------------------"
kcat -b "$KAFKA_SERVERS" -t "$TEST_TOPIC" -C -o -3 -e 2>/dev/null | jq -c . 2>/dev/null || \
kcat -b "$KAFKA_SERVERS" -t "$TEST_TOPIC" -C -o -3 -e 2>/dev/null
echo ""

# Summary
echo -e "${BLUE}🎯 Test Summary${NC}"
echo "==============="
echo -e "Kafka Server: ${YELLOW}$KAFKA_SERVERS${NC}"
echo -e "Test Topic: ${YELLOW}$TEST_TOPIC${NC}"
echo -e "Messages Sent: ${GREEN}$SENT_COUNT${NC}"
echo -e "Messages Received: ${GREEN}$RECEIVED_COUNT${NC}"

if [ "$SENT_COUNT" -eq 5 ] && [ "$RECEIVED_COUNT" -eq 5 ]; then
    echo -e "\n${GREEN}🎉 All tests PASSED! Your KRaft Kafka is working perfectly.${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests had issues. Check the output above.${NC}"
    exit 1
fi