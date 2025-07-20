# ChromaDB Deployment

This directory contains all the deployment files and scripts for ChromaDB in the Smart Campus Guide project.

## 📁 Directory Structure

```
deployment/
├── README.md                 # This file
├── CHROMADB_DEPLOYMENT.md   # Detailed deployment guide
├── kubernetes/              # Kubernetes manifests
│   ├── chromadb.yaml        # Main ChromaDB deployment
│   └── chromadb-ingress.yaml # Optional ingress configuration
├── scripts/                 # Deployment and utility scripts
│   ├── start-chromadb-complete.sh # Complete startup script
│   ├── port-forward-chromadb.sh   # Port forwarding script
│   └── test_chromadb.py     # Connectivity test script
└── dashboard/               # Web dashboard files
    ├── chromadb-dashboard.html    # Dashboard HTML
    └── serve-dashboard-with-proxy.py # Dashboard server with CORS proxy
```

## 🚀 Quick Start

### Using the Master Script (Recommended)

From the project root directory:

```bash
# Deploy ChromaDB to Kubernetes
./chromadb.sh deploy

# Start all services (port forwarding + dashboard)
./chromadb.sh start

# Check status
./chromadb.sh status

# Test connectivity
./chromadb.sh test

# Stop all services
./chromadb.sh stop
```

### Manual Deployment

1. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f deployment/kubernetes/chromadb.yaml
   ```

2. **Wait for pod to be ready:**
   ```bash
   kubectl wait --for=condition=ready pod -l app=chromadb --timeout=300s
   ```

3. **Start port forwarding:**
   ```bash
   ./deployment/scripts/port-forward-chromadb.sh
   ```

4. **Start dashboard (in another terminal):**
   ```bash
   python deployment/dashboard/serve-dashboard-with-proxy.py
   ```

## 🌐 Access Points

Once deployed and started:

- **Dashboard:** http://localhost:3001/chromadb-dashboard.html
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/heartbeat
- **Collections API:** http://localhost:8000/api/v1/collections

## 📋 Master Script Commands

| Command | Description |
|---------|-------------|
| `deploy` | Deploy ChromaDB to Kubernetes |
| `start` | Start port forwarding and dashboard |
| `stop` | Stop all services |
| `test` | Test ChromaDB connectivity |
| `dashboard` | Start only the dashboard |
| `status` | Show deployment status |
| `clean` | Remove ChromaDB deployment |
| `help` | Show help message |

## 🔧 Configuration

### ChromaDB Settings

The main configuration is in `kubernetes/chromadb.yaml`:

- **Version:** ChromaDB 0.5.23
- **Storage:** 2Gi persistent volume (hostpath)
- **Resources:** 512Mi-2Gi memory, 250m-1000m CPU
- **Health Checks:** Liveness, readiness, and startup probes
- **Services:** ClusterIP (internal) + NodePort (external on 30800)

### Dashboard Settings

The dashboard proxy server (`dashboard/serve-dashboard-with-proxy.py`):

- **Port:** 3001
- **CORS:** Enabled for all origins
- **Proxy:** Routes API calls to ChromaDB to avoid CORS issues

## 🛠️ Development

### Testing Changes

1. **Test connectivity:**
   ```bash
   ./chromadb.sh test
   ```

2. **Check logs:**
   ```bash
   kubectl logs -f statefulset/chromadb
   ```

3. **Manual API testing:**
   ```bash
   curl http://localhost:8000/api/v1/heartbeat
   ```

### Customization

- **Change storage size:** Edit `kubernetes/chromadb.yaml` PVC storage request
- **Change ports:** Update `DASHBOARD_PORT` in dashboard server
- **Add authentication:** Set `CHROMA_SERVER_AUTH_PROVIDER` in ConfigMap

## 🔒 Production Considerations

For production deployment:

1. **Security:**
   - Set `ALLOW_RESET: "false"` in ConfigMap
   - Enable authentication
   - Use proper TLS/HTTPS certificates
   - Restrict network policies

2. **Storage:**
   - Use proper storage class (not hostpath)
   - Configure backup strategies
   - Monitor disk usage

3. **Monitoring:**
   - Add Prometheus metrics
   - Set up alerting
   - Monitor resource usage

## 🐛 Troubleshooting

### Common Issues

1. **Pod not starting:**
   ```bash
   kubectl describe pod -l app=chromadb
   kubectl logs -l app=chromadb
   ```

2. **Storage issues:**
   ```bash
   kubectl describe pvc chromadb-pvc
   kubectl get storageclass
   ```

3. **Dashboard not loading:**
   - Check if port forwarding is active
   - Verify dashboard server is running on port 3001
   - Check browser console for errors

4. **API calls failing:**
   - Verify ChromaDB pod is running
   - Test direct API access: `curl http://localhost:8000/api/v1/heartbeat`
   - Check proxy server logs

### Getting Help

1. Check the detailed deployment guide: `CHROMADB_DEPLOYMENT.md`
2. Use the status command: `./chromadb.sh status`
3. Test connectivity: `./chromadb.sh test`
4. Check logs: `kubectl logs -f statefulset/chromadb`
