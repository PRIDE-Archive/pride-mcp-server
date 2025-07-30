# EBI Load Balancer Configuration Request

## Service Information

**Service Name:** PRIDE MCP Server  
**Team:** PRIDE Development Team  
**Contact:** [Your Name/Email]  
**Priority:** Medium  

## Request Summary

We need to add routing configuration to the EBI load balancer (`www.ebi.ac.uk`) for our new PRIDE MCP Server services. The services will be deployed on Kubernetes hosts (hh-wx machines) and need to be accessible under the `/pride/services/` path.

## Required Routes

Please add the following **SINGLE ROUTE** to the EBI load balancer configuration:

### 1. PRIDE Services (Single Entry Point)
- **Path:** `/pride/services/*`
- **Backend:** Kubernetes service endpoint (will be provided after deployment)
- **Port:** 80/443 (Ingress port)
- **Description:** **ALL** PRIDE services under this path - no additional EBI configuration needed for future services

### 2. Service Routing (Handled by Kubernetes Ingress)
The Kubernetes Ingress will handle all sub-path routing internally:

**Current Services:**
- **PRIDE MCP:** `/pride/services/pride-mcp/*` → MCP services
- **Web UI:** `/pride/services/pride-mcp/ui/*` → UI service
- **API:** `/pride/services/pride-mcp/api/*` → API service
- **Analytics:** `/pride/services/pride-mcp/analytics/*` → Analytics service

**Future Services (No EBI PR needed):**
- **PMultiQC:** `/pride/services/pmultiqc/*` → PMultiQC services
- **Other Services:** `/pride/services/service-name/*` → Any future service

## Key Benefit

**Only ONE EBI load balancer configuration needed** - all future services will be handled by the Kubernetes Ingress without requiring additional EBI team involvement.

## Technical Requirements

### SSL/TLS
- All routes should use HTTPS
- SSL termination handled by EBI load balancer
- Use existing EBI SSL certificates

### Headers
- Preserve original client headers
- Add `X-Forwarded-For` and `X-Real-IP` headers
- Support CORS headers for cross-origin requests

### Timeouts
- **Read Timeout:** 300 seconds (for long-running API calls)
- **Write Timeout:** 300 seconds
- **Idle Timeout:** 60 seconds

### Rate Limiting
- Standard EBI rate limiting policies
- Consider higher limits for API endpoints

## Backend Information

### Current Deployment
- **Namespace:** `pride-mcp`
- **Service Name:** `pride-mcp-server`
- **Kubernetes Cluster:** hh-wx machines
- **Load Balancer Type:** Internal Kubernetes load balancer

### Service Endpoints
The actual backend endpoints will be provided after the Kubernetes deployment is complete. The services will be accessible via:
- `pride-mcp-server-mcp-service.pride-mcp.svc.cluster.local:9000`
- `pride-mcp-server-ui-service.pride-mcp.svc.cluster.local:9090`
- `pride-mcp-server-analytics-service.pride-mcp.svc.cluster.local:8080`

## Testing

### Health Check Endpoints
- **Main Entry:** `/pride/services/` (should be accessible)
- **PRIDE MCP Root:** `/pride/services/pride-mcp/` (should redirect to UI)
- **Web UI:** `/pride/services/pride-mcp/ui/` (should serve HTML)
- **MCP Server:** `/pride/services/pride-mcp/mcp/` (should return 200 OK)
- **API:** `/pride/services/pride-mcp/api/health` (should return JSON health status)
- **Analytics:** `/pride/services/pride-mcp/analytics/` (should serve analytics dashboard)

### Expected Behavior
- All routes should return appropriate HTTP status codes
- CORS headers should be properly set for cross-origin requests
- SSL certificates should be valid and trusted
- Load balancing should distribute traffic across available backend instances

## Timeline

- **Request Date:** [Current Date]
- **Expected Deployment:** [Deployment Date]
- **Testing Period:** [Testing Period]
- **Go-Live:** [Go-Live Date]

## Contact Information

**Primary Contact:** [Your Name]  
**Email:** [Your Email]  
**Slack:** [Your Slack Handle]  
**Team:** PRIDE Development Team  

## Additional Notes

- These services are part of the PRIDE Archive ecosystem
- The MCP Server provides AI-powered access to PRIDE proteomics data
- Analytics dashboard tracks usage patterns and system performance
- Future services (PMultiQC) will be added incrementally
- All services follow EBI security and performance standards

---

**Please update this template with actual backend endpoints after Kubernetes deployment is complete.** 