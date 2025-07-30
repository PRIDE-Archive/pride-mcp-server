# Future Services Integration with Central Ingress

## 🎯 Central Ingress Strategy

### **Current Services (Already Configured)**
```yaml
# Single Ingress for all PRIDE services
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pride-services-ingress
  namespace: pride-mcp
spec:
  rules:
  - http:
      paths:
      # Current Services
      - path: /mcp(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-mcp-service
            port: 9000
      - path: /ui(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-ui-service
            port: 9090
      - path: /analytics(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-analytics-service
            port: 8080
      - path: /api(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-mcp-service
            port: 9000
      - path: /(.*)
        backend:
          service:
            name: pride-mcp-server-ui-service
            port: 9090
```

## 🆕 Adding Future Services

### **Example 1: PMultiQC Service**
```yaml
# Add to existing Ingress (NOT create new Ingress)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pride-services-ingress  # Same Ingress name
  namespace: pride-mcp
spec:
  rules:
  - http:
      paths:
      # Existing services...
      - path: /mcp(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-mcp-service
            port: 9000
      - path: /ui(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-ui-service
            port: 9090
      # NEW: PMultiQC Service
      - path: /pmultiqc(/|$)(.*)
        backend:
          service:
            name: pmultiqc-service
            port: 8000
      - path: /pmultiqc_ui(/|$)(.*)
        backend:
          service:
            name: pmultiqc-ui-service
            port: 8080
      # Default route
      - path: /(.*)
        backend:
          service:
            name: pride-mcp-server-ui-service
            port: 9090
```

### **Example 2: Multiple New Services**
```yaml
# Future expansion - all in one Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pride-services-ingress
  namespace: pride-mcp
spec:
  rules:
  - http:
      paths:
      # Core MCP Services
      - path: /mcp(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-mcp-service
            port: 9000
      - path: /ui(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-ui-service
            port: 9090
      - path: /analytics(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-analytics-service
            port: 8080
      - path: /api(/|$)(.*)
        backend:
          service:
            name: pride-mcp-server-mcp-service
            port: 9000
      
      # Analysis Services
      - path: /pmultiqc(/|$)(.*)
        backend:
          service:
            name: pmultiqc-service
            port: 8000
      - path: /pmultiqc_ui(/|$)(.*)
        backend:
          service:
            name: pmultiqc-ui-service
            port: 8080
      
      # Data Processing Services
      - path: /data_processor(/|$)(.*)
        backend:
          service:
            name: data-processor-service
            port: 7000
      - path: /data_processor_ui(/|$)(.*)
        backend:
          service:
            name: data-processor-ui-service
            port: 7070
      
      # Default route
      - path: /(.*)
        backend:
          service:
            name: pride-mcp-server-ui-service
            port: 9090
```

## 📋 Service Deployment Pattern

### **1. Deploy Service**
```yaml
# New service deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pmultiqc-service
  namespace: pride-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pmultiqc-service
  template:
    metadata:
      labels:
        app: pmultiqc-service
    spec:
      containers:
      - name: pmultiqc
        image: your-registry/pmultiqc:latest
        ports:
        - containerPort: 8000
```

### **2. Create Service**
```yaml
# Service for the deployment
apiVersion: v1
kind: Service
metadata:
  name: pmultiqc-service
  namespace: pride-mcp
spec:
  selector:
    app: pmultiqc-service
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

### **3. Update Ingress (Add Path)**
```yaml
# Add to existing Ingress (don't create new one)
- path: /pmultiqc(/|$)(.*)
  pathType: Prefix
  backend:
    service:
      name: pmultiqc-service
      port:
        number: 8000
```

## 🎯 Best Practices

### **✅ Do This:**
- Use **one central Ingress** for all services
- Add new paths to existing Ingress
- Use consistent naming conventions
- Group related services together
- Use path-based routing for organization

### **❌ Don't Do This:**
- Create separate Ingress for each service
- Use different Ingress classes
- Mix different SSL configurations
- Create inconsistent routing patterns

## 🔄 Deployment Workflow

### **For New Services:**
1. **Deploy Service**: Create Deployment and Service
2. **Update Ingress**: Add new path to central Ingress
3. **Test Routing**: Verify internal routing works
4. **Update EBI Team**: Add new external path to load balancer
5. **Test End-to-End**: Verify external access works

### **Example Commands:**
```bash
# Deploy new service
kubectl apply -f pmultiqc-deployment.yaml
kubectl apply -f pmultiqc-service.yaml

# Update Ingress (add new path)
kubectl apply -f updated-ingress.yaml

# Test internal routing
curl http://cluster-ip:port/pmultiqc/health

# After EBI configuration
curl https://www.ebi.ac.uk/pride/services/pmultiqc/health
```

## 📊 Benefits Summary

| Aspect | Multiple Ingress | Central Ingress |
|--------|------------------|-----------------|
| **Management** | Complex | Simple |
| **Configuration** | Inconsistent | Consistent |
| **Resource Usage** | High | Low |
| **Maintenance** | Difficult | Easy |
| **Monitoring** | Scattered | Centralized |
| **SSL/TLS** | Multiple configs | Single config |
| **CORS** | Per-service | Global |

## 🎉 Conclusion

**Stick with your current central Ingress approach!** It's the right strategy for:
- Scalability
- Maintainability  
- Consistency
- Resource efficiency

When you add PMultiQC or other services, just add new paths to your existing Ingress rather than creating separate Ingress resources. 