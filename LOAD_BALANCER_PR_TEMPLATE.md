# EBI Load Balancer Configuration Request

## Service Information

**Service Name:** PRIDE MCP Server  
**Team:** PRIDE Development Team  
**Contact:** [Your Name/Email]  
**Priority:** Medium  

## Request Summary

We need to add routing configuration to the EBI load balancer (`www.ebi.ac.uk`) for our new PRIDE MCP Server services. The services will be deployed on Kubernetes hosts (hh-wx machines) and need to be accessible under the `/pride/services/` path.

## Required Routes

Please add the following routes to the EBI load balancer configuration:

### 1. MCP Server Endpoint
- **Path:** `/pride/services/mcp`
- **Backend:** Kubernetes service endpoint (will be provided after deployment)
- **Port:** 9000
- **Description:** Model Context Protocol server for PRIDE Archive data access

### 2. Web UI
- **Path:** `/pride/services/mcp_ui`
- **Backend:** Kubernetes service endpoint (will be provided after deployment)
- **Port:** 9090
- **Description:** Professional web interface for PRIDE MCP Server

### 3. Analytics Dashboard
- **Path:** `/pride/services/mcp_analysis_ui`
- **Backend:** Kubernetes service endpoint (will be provided after deployment)
- **Port:** 8080
- **Description:** Analytics dashboard for monitoring service usage

### 4. API Endpoints
- **Path:** `/pride/services/mcp_api`
- **Backend:** Kubernetes service endpoint (will be provided after deployment)
- **Port:** 9000
- **Description:** REST API endpoints for analytics and system management

## Future Services (To be added later)

### 5. PMultiQC Service
- **Path:** `/pride/services/pmultiqc`
- **Backend:** TBD
- **Port:** TBD
- **Description:** PMultiQC service for proteomics data analysis

### 6. PMultiQC UI
- **Path:** `/pride/services/pmultiqc_ui`
- **Backend:** TBD
- **Port:** TBD
- **Description:** PMultiQC web interface

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
- **MCP Server:** `/pride/services/mcp/` (should return 200 OK)
- **Web UI:** `/pride/services/mcp_ui/` (should serve HTML)
- **API:** `/pride/services/mcp_api/health` (should return JSON health status)
- **Analytics:** `/pride/services/mcp_analysis_ui/` (should serve analytics dashboard)

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