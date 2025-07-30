# PRIDE MCP Server - Kubernetes Deployment Guide

## Prerequisites

1. **Kubernetes Cluster** with:
   - NGINX Ingress Controller
   - Access to EBI PRIDE load balancer
   - GitLab Container Registry access

2. **GitLab CI/CD Variables**:
   - `CI_REGISTRY_IMAGE`: Your GitLab registry image path
   - `KUBE_CONFIG`: Base64 encoded Kubernetes config
   - `CI_DEPLOY_USER`: GitLab registry username
   - `CI_DEPLOY_PASSWORD`: GitLab registry password
   - `GEMINI_API_KEY_B64`: (Optional) Base64 encoded Gemini AI API key
   - `INGRESS_HOST`: EBI domain (www.ebi.ac.uk)

## Setup Steps

### 1. Configure GitLab CI/CD Variables

Go to your GitLab project → Settings → CI/CD → Variables and add:

```
CI_REGISTRY_IMAGE = registry.gitlab.com/your-username/pride-mcp-server
KUBE_CONFIG = <base64-encoded-kubeconfig>
CI_DEPLOY_USER = gitlab-ci-token
CI_DEPLOY_PASSWORD = <your-gitlab-token>
GEMINI_API_KEY_B64 = <base64-encoded-api-key>
INGRESS_HOST = www.ebi.ac.uk
```

### 2. Update Domain Configuration

Edit `k8s/ingress.yaml`:
```yaml
hosts:
  - pride-mcp.your-domain.com  # Replace with your domain
```

### 3. Configure API Keys

Edit `k8s/secret.yaml`:
```yaml
data:
  GEMINI_API_KEY: "base64-encoded-api-key"
  OPENAI_API_KEY: "base64-encoded-api-key"
  CLAUDE_API_KEY: "base64-encoded-api-key"
```

To encode your API key:
```bash
echo -n "your-api-key" | base64
```

### 4. Deploy to Kubernetes

The deployment will happen automatically when you push to the `main` branch, or you can manually trigger it from GitLab CI/CD.

### 5. Verify Deployment

```bash
# Check namespace
kubectl get namespace pride-mcp

# Check pods
kubectl get pods -n pride-mcp

# Check services
kubectl get services -n pride-mcp

# Check ingress
kubectl get ingress -n pride-mcp

# Check logs
kubectl logs -f deployment/pride-mcp-server -n pride-mcp
```

## Access Points

All services are accessible under the EBI PRIDE domain with different paths:

- **Web UI (Main)**: `https://www.ebi.ac.uk/pride/services/mcp_ui/`
- **MCP Server**: `https://www.ebi.ac.uk/pride/services/mcp/`
- **API Endpoints**: `https://www.ebi.ac.uk/pride/services/mcp_api/`
- **Analytics Dashboard**: `https://www.ebi.ac.uk/pride/services/mcp_analysis_ui/`
- **API Documentation**: `https://www.ebi.ac.uk/pride/services/mcp_api/docs`

## Load Balancer Configuration

The services are integrated with the main EBI load balancer at `www.ebi.ac.uk`. Use the `LOAD_BALANCER_PR_TEMPLATE.md` file to create a pull request for the EBI service team to configure the routing.

## Monitoring

### Health Checks
- Liveness probe: `/mcp/` endpoint
- Readiness probe: `/mcp/` endpoint
- Startup probe: `/mcp/` endpoint

### Resource Limits
- CPU: 500m (0.5 cores)
- Memory: 512Mi

### Scaling
The deployment is configured with 2 replicas by default. You can scale it:

```bash
kubectl scale deployment pride-mcp-server --replicas=3 -n pride-mcp
```

## Troubleshooting

### Check Pod Status
```bash
kubectl describe pod -l app=pride-mcp-server -n pride-mcp
```

### Check Logs
```bash
kubectl logs -f deployment/pride-mcp-server -n pride-mcp
```

### Check Ingress
```bash
kubectl describe ingress pride-mcp-ingress -n pride-mcp
```

### Common Issues

1. **Image Pull Errors**: Ensure GitLab registry credentials are configured
2. **API Key Issues**: Verify secrets are properly base64 encoded
3. **Ingress Issues**: Check NGINX ingress controller and cert-manager
4. **Resource Issues**: Monitor CPU and memory usage

## Security Notes

- API keys are stored as Kubernetes secrets
- HTTPS is enforced via cert-manager
- Non-root user runs the application
- Resource limits prevent resource exhaustion 