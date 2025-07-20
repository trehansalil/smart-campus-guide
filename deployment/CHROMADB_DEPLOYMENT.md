# ChromaDB Kubernetes Deployment Guide

## ✅ Deployment Status: COMPLETED SUCCESSFULLY!

Your ChromaDB is now running and accessible! 🎉

**🎯 All Dashboard Functions Working:**
- ✅ Service Status (Online/Offline indicator)
- ✅ Health Check & Version Info
- ✅ Collections Management (List, Create, Delete)
- ✅ Database Reset Functionality
- ✅ API Documentation Links (Open API Docs & OpenAPI JSON)
- ✅ Quick Actions (Create/Delete Test Collections)
- ✅ CORS Issues Resolved with Proxy Server

## ⚡ Quick Start (TL;DR)

### Option 1: Complete Startup (Recommended)
```bash
# From project root
./chromadb.sh start
```
This single command handles everything: pod check, port forwarding, dashboard server, and opens the browser.

### Option 2: Master Script Commands
```bash
./chromadb.sh deploy    # Deploy to Kubernetes
./chromadb.sh start     # Start all services  
./chromadb.sh status    # Check status
./chromadb.sh test      # Test connectivity
./chromadb.sh stop      # Stop services
```

### Option 3: Manual Steps
1. **Ensure ChromaDB is running:**
   ```bash
   kubectl get pods -l app=chromadb
   ```

2. **Start port forwarding (if not already running):**
   ```bash
   ./deployment/scripts/port-forward-chromadb.sh
   ```

3. **Launch the dashboard with CORS proxy:**
   ```bash
   python deployment/dashboard/serve-dashboard-with-proxy.py
   ```

4. **Access the dashboard:** http://localhost:3001/chromadb-dashboard.html

## 🚀 Quick Deployment

1. **Deploy ChromaDB to your cluster:**
   ```bash
   kubectl apply -f deployment/kubernetes/chromadb.yaml
   ```

2. **Check deployment status:**
   ```bash
   kubectl get pods -l app=chromadb
   kubectl get services -l app=chromadb
   kubectl get pvc chromadb-pvc
   ```

3. **Wait for the pod to be ready:**
   ```bash
   kubectl wait --for=condition=ready pod -l app=chromadb --timeout=300s
   ```

## 🌐 Accessing ChromaDB UI

### ⭐ Method 1: Port Forwarding (ACTIVE - Recommended for Development)
```bash
# Using the provided script (CURRENTLY RUNNING)
./port-forward-chromadb.sh

# Or manually
kubectl port-forward service/chromadb 8000:8000
```

**🌐 Access URLs (Available Now):**
- **API Documentation (Swagger UI):** http://localhost:8000/docs  
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **Health Check:** http://localhost:8000/api/v1/heartbeat
- **Collections API:** http://localhost:8000/api/v1/collections
- **Version Info:** http://localhost:8000/api/v1/version

⚠️ **Note:** ChromaDB doesn't have a traditional web UI at the root path (`/`). It's an API service - use `/docs` for the interactive API documentation!

### Method 2: NodePort Service (Available)
```bash
# Get the node IP and access via NodePort
kubectl get nodes -o wide
# Access via: http://<NODE_IP>:30800
```

### Method 3: Ingress (Optional - requires ingress controller)
```bash
# Deploy ingress (if you have nginx-ingress or similar)
kubectl apply -f deployment/kubernetes/chromadb-ingress.yaml

# Add to /etc/hosts (for local testing)
echo "127.0.0.1 chromadb.local" | sudo tee -a /etc/hosts

# Access via: http://chromadb.local
```

## 🔧 Configuration Improvements Made

1. **Resource Management:**
   - Added CPU/Memory requests and limits
   - Storage: 2Gi hostpath (matching your environment)

2. **Health Checks:**
   - Liveness probe for container health
   - Readiness probe for traffic routing
   - Startup probe for initial startup

3. **Configuration Management:**
   - Added ConfigMap for environment variables
   - Pinned to specific ChromaDB version (0.5.23)

4. **Network Access:**
   - ClusterIP service for internal access
   - NodePort service for external access (port 30800)
   - Optional Ingress for domain-based access

5. **Custom Dashboard:**
   - Created `chromadb-dashboard.html` for easy web interface
   - Interactive API testing and collection management

## 🔍 Useful Commands

### Check logs:
```bash
kubectl logs -f statefulset/chromadb
```

### Check ChromaDB status:
```bash
curl http://localhost:8000/api/v1/heartbeat
```

### List collections (after port-forward):
```bash
curl http://localhost:8000/api/v1/collections
```

### Create a test collection:
```bash
curl -X POST http://localhost:8000/api/v1/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "test_collection", "metadata": {"description": "Test collection"}}'
```

### Reset database (if ALLOW_RESET=true):
```bash
curl -X POST http://localhost:8000/api/v1/reset
```

## 🌐 Web Interfaces

### ⭐ Recommended: Custom Dashboard with CORS Proxy
```bash
# Start the dashboard server with CORS proxy (RECOMMENDED)
python serve-dashboard-with-proxy.py
```
Then access: **http://localhost:3001/chromadb-dashboard.html**

### Alternative: Basic Dashboard Server
```bash
# Start the basic dashboard server (may have CORS issues)
python serve-dashboard.py
```
Then access: **http://localhost:3000/chromadb-dashboard.html**

### Alternative Access Methods:
1. **API Documentation:** http://localhost:8000/docs (Swagger UI)
2. **OpenAPI JSON:** http://localhost:8000/openapi.json
3. **Direct API calls:** Use curl or programming languages

✅ **Note:** The CORS proxy version (`serve-dashboard-with-proxy.py`) is recommended as it properly handles all API operations including POST/DELETE requests!

## 🐛 Troubleshooting

### Pod not starting:
```bash
kubectl describe pod -l app=chromadb
kubectl logs -l app=chromadb
```

### Storage issues:
```bash
kubectl describe pvc chromadb-pvc
kubectl get storageclass
```

### Network issues:
```bash
kubectl get endpoints chromadb
kubectl describe service chromadb
```

## 🔒 Security Considerations

For production deployment:
1. Set `ALLOW_RESET: "false"` in ConfigMap
2. Enable authentication by setting `CHROMA_SERVER_AUTH_PROVIDER`
3. Use TLS/HTTPS with proper certificates
4. Restrict network policies
5. Use secrets for sensitive configuration

## 📊 Monitoring

The deployment includes health check endpoints:
- `/api/v1/heartbeat` - Basic health check
- `/api/v1/version` - Version information
- Monitor pod metrics with your monitoring solution
