# Routing Architecture for EBI Infrastructure

## 🌐 Two-Level Routing System

```
Internet User
    ↓
EBI Load Balancer (www.ebi.ac.uk)
    ↓ (ONE TIME setup: /pride/services/* → Your cluster)
Kubernetes Cluster (hh-wx machines)
    ↓ (Your internal Ingress handles ALL sub-routing)
Individual Services
```

## 🔄 Traffic Flow

### **Level 1: EBI Load Balancer (External)**
```
User Request: https://www.ebi.ac.uk/pride/services/pride-mcp/ui/
    ↓
EBI Load Balancer routes ALL /pride/services/* to your Kubernetes cluster
    ↓
Internal Request: http://your-cluster-ip:port/pride/services/pride-mcp/ui/
```

### **Level 2: Kubernetes Ingress (Internal)**
```
Internal Request: http://your-cluster-ip:port/pride/services/pride-mcp/ui/
    ↓
Kubernetes Ingress (nginx) processes path and routes to specific service
    ↓
Routes to UI service: http://ui-service:9090/ui/
```

## 📋 Path Routing Table

| External URL | Internal Path | Service | Port | Purpose |
|--------------|---------------|---------|------|---------|
| `/pride/services/pride-mcp/ui/` | `/pride-mcp/ui/` | UI Service | 9090 | Web Interface |
| `/pride/services/pride-mcp/mcp/` | `/pride-mcp/mcp/` | MCP Service | 9000 | MCP Protocol |
| `/pride/services/pride-mcp/api/` | `/pride-mcp/api/` | MCP Service | 9000 | REST API |
| `/pride/services/pride-mcp/analytics/` | `/pride-mcp/analytics/` | Analytics Service | 8080 | Analytics Dashboard |
| `/pride/services/pride-mcp/` | `/pride-mcp/` | UI Service | 9090 | Default (UI) |

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
External: https://www.ebi.ac.uk/pride/services/pride-mcp/ui/dashboard
    ↓ (EBI Load Balancer)
Internal: http://cluster-ip:port/pride-mcp/ui/dashboard
    ↓ (Kubernetes Ingress - path: /pride-mcp/ui(/|$)(.*))
Internal: http://ui-service:9090/dashboard
```

### **Example 2: API Access**
```
External: https://www.ebi.ac.uk/pride/services/pride-mcp/api/health
    ↓ (EBI Load Balancer)
Internal: http://cluster-ip:port/pride-mcp/api/health
    ↓ (Kubernetes Ingress - path: /pride-mcp/api(/|$)(.*))
Internal: http://mcp-service:9000/api/health
```

### **Example 3: MCP Protocol**
```
External: https://www.ebi.ac.uk/pride/services/pride-mcp/mcp/
    ↓ (EBI Load Balancer)
Internal: http://cluster-ip:port/pride-mcp/mcp/
    ↓ (Kubernetes Ingress - path: /pride-mcp/mcp(/|$)(.*))
Internal: http://mcp-service:9000/
```

## 🎯 Key Benefits

1. **Separation of Concerns**: EBI handles external routing, you handle internal routing
2. **Scalability**: Easy to add new services under `/pride/services/` **without EBI involvement**
3. **Security**: SSL termination at EBI level
4. **Flexibility**: Internal paths can be different from external paths
5. **Maintenance**: Each team manages their own routing layer
6. **Future-Proof**: **Only ONE EBI configuration needed** - all future services handled by Kubernetes Ingress

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
curl http://cluster-ip:port/pride-mcp/ui/
curl http://cluster-ip:port/pride-mcp/mcp/
curl http://cluster-ip:port/pride-mcp/api/health
curl http://cluster-ip:port/pride-mcp/analytics/
```

### **External Testing (After EBI Setup)**
```bash
# Test external routing
curl https://www.ebi.ac.uk/pride/services/pride-mcp/ui/
curl https://www.ebi.ac.uk/pride/services/pride-mcp/mcp/
curl https://www.ebi.ac.uk/pride/services/pride-mcp/api/health
curl https://www.ebi.ac.uk/pride/services/pride-mcp/analytics/
```

## 🚀 Future Services Pattern

When adding new services, follow the same hierarchical pattern:

```
https://www.ebi.ac.uk/pride/services/
├── pride-mcp/                    # Current service
│   ├── ui/
│   ├── mcp/
│   ├── api/
│   └── analytics/
├── pmultiqc/                     # Future service
│   ├── ui/
│   ├── service/
│   └── api/
└── other-service/                # Another future service
    ├── ui/
    ├── api/
    └── dashboard/
```

### **Consistent Pattern for All Services:**

| Service | Parent Path | Sub-paths | Description |
|---------|-------------|-----------|-------------|
| **PRIDE MCP** | `/pride/services/pride-mcp/` | `/ui/`, `/mcp/`, `/api/`, `/analytics/` | Current MCP services |
| **PMultiQC** | `/pride/services/pmultiqc/` | `/ui/`, `/service/`, `/api/` | Future proteomics QC |
| **Service X** | `/pride/services/service-x/` | `/ui/`, `/api/`, `/dashboard/` | Any future service |

## 📝 Notes

- **Path Rewriting**: The `rewrite-target: /$2` removes the prefix and passes the rest to the service
- **CORS**: Internal CORS headers are added by Kubernetes Ingress
- **SSL**: SSL termination happens at EBI level, internal traffic is HTTP
- **Health Checks**: Each service should have health check endpoints
- **Logging**: Both EBI and Kubernetes Ingress provide access logs
- **Consistency**: All future services follow the same parent path + sub-paths pattern 