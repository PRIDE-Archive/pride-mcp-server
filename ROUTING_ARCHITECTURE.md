# Routing Architecture for EBI Infrastructure

## 🌐 Two-Level Routing System

```
Internet User
    ↓
EBI Load Balancer (www.ebi.ac.uk)
    ↓ (Configured by EBI team via PR)
Kubernetes Cluster (hh-wx machines)
    ↓ (Your internal Ingress)
Individual Services
```

## 🔄 Traffic Flow

### **Level 1: EBI Load Balancer (External)**
```
User Request: https://www.ebi.ac.uk/pride/services/mcp_ui/
    ↓
EBI Load Balancer routes to your Kubernetes cluster
    ↓
Internal Request: http://your-cluster-ip:port/
```

### **Level 2: Kubernetes Ingress (Internal)**
```
Internal Request: http://your-cluster-ip:port/mcp_ui/
    ↓
Kubernetes Ingress (nginx) processes path
    ↓
Routes to specific service based on path
```

## 📋 Path Routing Table

| External URL | Internal Path | Service | Port | Purpose |
|--------------|---------------|---------|------|---------|
| `/pride/services/mcp_ui/` | `/ui/` | UI Service | 9090 | Web Interface |
| `/pride/services/mcp/` | `/mcp/` | MCP Service | 9000 | MCP Protocol |
| `/pride/services/mcp_api/` | `/api/` | MCP Service | 9000 | REST API |
| `/pride/services/mcp_analysis_ui/` | `/analytics/` | Analytics Service | 8080 | Analytics Dashboard |
| `/pride/services/` | `/` | UI Service | 9090 | Default (UI) |

## ⚙️ Configuration Details

### **EBI Load Balancer (Managed by EBI Team)**
- **Domain**: `www.ebi.ac.uk`
- **Base Path**: `/pride/services/`
- **SSL/TLS**: Handled by EBI
- **CORS**: Handled by EBI
- **Rate Limiting**: Handled by EBI

### **Kubernetes Ingress (Your Configuration)**
- **Ingress Class**: `nginx`
- **Path Rewriting**: `nginx.ingress.kubernetes.io/rewrite-target: /$2`
- **CORS**: Internal CORS headers
- **Timeouts**: 300s for long operations
- **Body Size**: 10MB limit

## 🔧 How Path Rewriting Works

### **Example 1: Web UI Access**
```
External: https://www.ebi.ac.uk/pride/services/mcp_ui/dashboard
    ↓ (EBI Load Balancer)
Internal: http://cluster-ip:port/mcp_ui/dashboard
    ↓ (Kubernetes Ingress - path: /mcp_ui(/|$)(.*))
Internal: http://ui-service:9090/dashboard
```

### **Example 2: API Access**
```
External: https://www.ebi.ac.uk/pride/services/mcp_api/health
    ↓ (EBI Load Balancer)
Internal: http://cluster-ip:port/mcp_api/health
    ↓ (Kubernetes Ingress - path: /api(/|$)(.*))
Internal: http://mcp-service:9000/api/health
```

### **Example 3: MCP Protocol**
```
External: https://www.ebi.ac.uk/pride/services/mcp/
    ↓ (EBI Load Balancer)
Internal: http://cluster-ip:port/mcp/
    ↓ (Kubernetes Ingress - path: /mcp(/|$)(.*))
Internal: http://mcp-service:9000/
```

## 🎯 Key Benefits

1. **Separation of Concerns**: EBI handles external routing, you handle internal routing
2. **Scalability**: Easy to add new services under `/pride/services/`
3. **Security**: SSL termination at EBI level
4. **Flexibility**: Internal paths can be different from external paths
5. **Maintenance**: Each team manages their own routing layer

## 🚀 Deployment Process

1. **Deploy to Kubernetes**: Your services are accessible internally
2. **Test Internal Routing**: Verify Ingress routes correctly
3. **Provide Endpoints to EBI**: Give them your cluster endpoints
4. **EBI Configures Load Balancer**: They route external traffic to your cluster
5. **Test End-to-End**: Verify external URLs work correctly

## 🔍 Testing Commands

### **Internal Testing (Before EBI Setup)**
```bash
# Test internal routing
curl http://cluster-ip:port/ui/
curl http://cluster-ip:port/mcp/
curl http://cluster-ip:port/api/health
curl http://cluster-ip:port/analytics/
```

### **External Testing (After EBI Setup)**
```bash
# Test external routing
curl https://www.ebi.ac.uk/pride/services/mcp_ui/
curl https://www.ebi.ac.uk/pride/services/mcp/
curl https://www.ebi.ac.uk/pride/services/mcp_api/health
curl https://www.ebi.ac.uk/pride/services/mcp_analysis_ui/
```

## 📝 Notes

- **Path Rewriting**: The `rewrite-target: /$2` removes the prefix and passes the rest to the service
- **CORS**: Internal CORS headers are added by Kubernetes Ingress
- **SSL**: SSL termination happens at EBI level, internal traffic is HTTP
- **Health Checks**: Each service should have health check endpoints
- **Logging**: Both EBI and Kubernetes Ingress provide access logs 