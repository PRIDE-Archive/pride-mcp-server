#!/bin/bash

# PRIDE MCP Server Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 PRIDE MCP Server Deployment${NC}"

# Check if namespace exists, create if it doesn't
NAMESPACE="pride-mcp"
if ! kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Creating namespace: $NAMESPACE${NC}"
    kubectl create namespace $NAMESPACE
    echo -e "${GREEN}✅ Namespace created successfully${NC}"
else
    echo -e "${GREEN}✅ Namespace $NAMESPACE already exists${NC}"
fi

# Deploy the application
echo -e "${YELLOW}📦 Deploying PRIDE MCP Server...${NC}"
kubectl apply -f .kubernetes.yml

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

# Show deployment status
echo -e "${YELLOW}📊 Deployment Status:${NC}"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "  1. Wait for pods to be ready: kubectl get pods -n $NAMESPACE -w"
echo -e "  2. Check logs: kubectl logs -n $NAMESPACE -l app=pride-mcp-server"
echo -e "  3. Test internal endpoints (before EBI setup)"
echo -e "  4. Create EBI load balancer PR using LOAD_BALANCER_PR_TEMPLATE.md" 