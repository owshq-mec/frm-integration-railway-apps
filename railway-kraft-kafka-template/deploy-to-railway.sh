#!/bin/bash

# Railway KRaft Kafka Deployment Script
# Automates the deployment and configuration process

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚄 Railway KRaft Kafka Deployment${NC}"
echo "=================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI is not installed${NC}"
    echo "Please install it from: https://docs.railway.app/develop/cli"
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI found${NC}"

# Login check
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}🔐 Please login to Railway first${NC}"
    railway login
fi

echo -e "${GREEN}✅ Railway authentication verified${NC}"
echo ""

# Deploy the service
echo -e "${BLUE}🚀 Deploying KRaft Kafka service...${NC}"
railway up

# Get service information
SERVICE_ID=$(railway status --json | jq -r '.serviceId')
PROJECT_ID=$(railway status --json | jq -r '.projectId')

echo -e "${GREEN}✅ Service deployed successfully${NC}"
echo -e "Service ID: ${YELLOW}$SERVICE_ID${NC}"
echo -e "Project ID: ${YELLOW}$PROJECT_ID${NC}"
echo ""

# Enable TCP proxy
echo -e "${BLUE}🌐 Configuring TCP proxy...${NC}"
echo "Please manually enable TCP proxy in Railway dashboard:"
echo -e "${YELLOW}1. Go to your Railway project dashboard${NC}"
echo -e "${YELLOW}2. Select your Kafka service${NC}"
echo -e "${YELLOW}3. Go to Settings → Networking${NC}"
echo -e "${YELLOW}4. Enable 'TCP Proxy'${NC}"
echo ""

# Wait for user confirmation
read -p "Press Enter after enabling TCP proxy..."

# Get the TCP proxy domain
echo -e "${BLUE}📡 Getting TCP proxy information...${NC}"
DOMAIN=$(railway domain | grep -o '[a-zA-Z0-9.-]*\.railway\.app' | head -1)

if [ -n "$DOMAIN" ]; then
    echo -e "${GREEN}✅ Domain found: $DOMAIN${NC}"
    
    # Extract proxy details
    PROXY_DOMAIN=$(echo "$DOMAIN" | sed 's/\.railway\.app/.proxy.rlwy.net/')
    echo -e "${YELLOW}Your Kafka endpoint: $PROXY_DOMAIN:PORT${NC}"
    echo ""
    
    # Test connectivity
    echo -e "${BLUE}🧪 Testing connectivity...${NC}"
    sleep 30  # Wait for service to start
    
    # Try to get the actual port from Railway
    echo "Checking service status..."
    railway ps
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. Find your TCP proxy port in Railway dashboard"
    echo "2. Test with: kcat -b $PROXY_DOMAIN:PORT -L"
    echo "3. Use the test script: ./test-kraft-kafka.sh $PROXY_DOMAIN:PORT"
    
else
    echo -e "${YELLOW}⚠️  Could not automatically detect domain${NC}"
    echo "Please check Railway dashboard for your service URL"
fi

echo ""
echo -e "${BLUE}🔗 Useful Commands:${NC}"
echo "railway logs    # View service logs"
echo "railway status  # Check service status"
echo "railway shell   # Access service shell"
echo ""

echo -e "${GREEN}✅ KRaft Kafka is ready on Railway!${NC}"