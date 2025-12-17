#!/bin/bash

# Quick test script for PoC UI

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Quick PoC UI Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test API health
echo -e "${YELLOW}Testing API health...${NC}"
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API server is running${NC}"
else
    echo -e "${RED}✗ API server is not running${NC}"
    echo -e "   Start it with: cd ui-poc-api && python app.py"
    exit 1
fi

# Test API endpoints
echo -e "${YELLOW}Testing API endpoints...${NC}"

# Test archive statistics
if curl -s http://localhost:5001/api/archive/statistics > /dev/null 2>&1; then
    echo -e "${GREEN}✓ /api/archive/statistics${NC}"
else
    echo -e "${RED}✗ /api/archive/statistics failed${NC}"
fi

# Test contributions
if curl -s http://localhost:5001/api/archive/contributions > /dev/null 2>&1; then
    echo -e "${GREEN}✓ /api/archive/contributions${NC}"
else
    echo -e "${RED}✗ /api/archive/contributions failed${NC}"
fi

# Test sandbox map
if curl -s http://localhost:5001/api/sandbox-map > /dev/null 2>&1; then
    echo -e "${GREEN}✓ /api/sandbox-map${NC}"
else
    echo -e "${RED}✗ /api/sandbox-map failed${NC}"
fi

# Test frontend
echo -e "${YELLOW}Testing frontend...${NC}"
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not running${NC}"
    echo -e "   Start it with: cd ui-poc && npm run dev"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Basic connectivity tests passed!${NC}"
echo ""
echo -e "Next steps:"
echo -e "1. Open ${BLUE}http://localhost:3000${NC} in your browser"
echo -e "2. Navigate to Dashboard to see statistics"
echo -e "3. Submit a test contribution"
echo -e "4. Explore the Sandbox Map"
echo ""
