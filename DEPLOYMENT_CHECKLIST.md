# EBI Deployment Checklist

## Pre-Deployment

### 1. Infrastructure Setup
- [ ] Kubernetes cluster access confirmed (hh-wx machines)
- [ ] GitLab CI/CD variables configured
- [ ] Docker registry access verified
- [ ] Namespace `pride-mcp` created

### 2. Configuration
- [ ] `config.env` updated with production settings
- [ ] `GEMINI_API_KEY` configured (optional)
- [ ] `SLACK_WEBHOOK_URL` configured (optional)
- [ ] Database path configured for persistent storage

### 3. Load Balancer Request
- [ ] `LOAD_BALANCER_PR_TEMPLATE.md` filled out with contact information
- [ ] Pull request created for EBI service team
- [ ] Backend endpoints documented for load balancer team
- [ ] Timeline agreed with service team

## Deployment

### 1. Kubernetes Deployment
- [ ] GitLab CI/CD pipeline triggered
- [ ] Docker image built and pushed successfully
- [ ] Kubernetes manifests applied
- [ ] Pods running and healthy
- [ ] Services created and accessible

### 2. Service Verification
- [ ] MCP Server responding on port 9000
- [ ] Web UI accessible on port 9090
- [ ] Analytics service running on port 8080
- [ ] API endpoints responding correctly
- [ ] Database initialized and working

### 3. Load Balancer Integration
- [ ] EBI service team configured routing
- [ ] SSL certificates applied
- [ ] CORS headers configured
- [ ] Health checks passing
- [ ] All paths accessible via EBI domain

## Post-Deployment

### 1. Testing
- [ ] All services accessible via EBI URLs
- [ ] MCP protocol working correctly
- [ ] Web UI functional
- [ ] Analytics dashboard displaying data
- [ ] API endpoints responding
- [ ] Database storing questions correctly

### 2. Monitoring
- [ ] Logs being collected
- [ ] Metrics available
- [ ] Alerts configured
- [ ] Performance monitoring active
- [ ] Error tracking enabled

### 3. Documentation
- [ ] User documentation updated
- [ ] API documentation accessible
- [ ] Integration guides updated
- [ ] Troubleshooting guide created
- [ ] Contact information published

## URLs to Test

### Production URLs (After Load Balancer Setup)
- [ ] `https://www.ebi.ac.uk/pride/services/mcp_ui/` - Web UI
- [ ] `https://www.ebi.ac.uk/pride/services/mcp/` - MCP Server
- [ ] `https://www.ebi.ac.uk/pride/services/mcp_api/health` - Health Check
- [ ] `https://www.ebi.ac.uk/pride/services/mcp_analysis_ui/` - Analytics Dashboard
- [ ] `https://www.ebi.ac.uk/pride/services/mcp_api/docs` - API Documentation

### Internal URLs (For Testing)
- [ ] `http://<internal-ip>:30990/` - Web UI (NodePort)
- [ ] `http://<internal-ip>:30900/` - MCP Server (NodePort)
- [ ] `http://<internal-ip>:30900/api/health` - API Health Check

## Future Services

### PMultiQC Integration
- [ ] PMultiQC service developed
- [ ] PMultiQC UI created
- [ ] Load balancer configuration updated
- [ ] New paths added to EBI routing
- [ ] Testing completed

## Rollback Plan

### If Issues Occur
1. **Immediate Rollback**: Revert to previous Docker image
2. **Load Balancer Rollback**: Disable new routes temporarily
3. **Database Backup**: Ensure data is backed up before changes
4. **Communication**: Notify stakeholders of any issues

## Contact Information

**Primary Contact:** [Your Name]  
**Email:** [Your Email]  
**Slack:** [Your Slack Handle]  
**Team:** PRIDE Development Team  

**EBI Service Team:** [Service Team Contact]  
**Load Balancer Team:** [Load Balancer Team Contact]  

---

**Last Updated:** [Date]  
**Version:** 1.0 