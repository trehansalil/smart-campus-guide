#!/bin/bash

# ChromaDB Complete Startup Script
# This script starts both port forwarding and the dashboard server

echo "🚀 ChromaDB Complete Startup Script"
echo "=================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to check if ChromaDB pod is running
check_chromadb_pod() {
    local pod_status=$(kubectl get pods -l app=chromadb -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
    if [ "$pod_status" = "Running" ]; then
        return 0
    else
        return 1
    fi
}

# Step 1: Check if ChromaDB pod is running
echo "1️⃣ Checking ChromaDB pod status..."
if check_chromadb_pod; then
    echo "   ✅ ChromaDB pod is running"
else
    echo "   ❌ ChromaDB pod is not running"
    echo "   💡 Try: kubectl apply -f deployment/kubernetes/chromadb.yaml"
    echo "   💡 Check status: kubectl get pods -l app=chromadb"
    exit 1
fi

# Step 2: Check/Start port forwarding
echo ""
echo "2️⃣ Setting up port forwarding..."
if check_port 8000; then
    echo "   ✅ Port 8000 is already in use (port forwarding likely active)"
else
    echo "   🔄 Starting port forwarding..."
    kubectl port-forward service/chromadb 8000:8000 &
    PORT_FORWARD_PID=$!
    sleep 2
    
    if check_port 8000; then
        echo "   ✅ Port forwarding started (PID: $PORT_FORWARD_PID)"
    else
        echo "   ❌ Failed to start port forwarding"
        exit 1
    fi
fi

# Step 3: Test ChromaDB API
echo ""
echo "3️⃣ Testing ChromaDB API..."
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null; then
    echo "   ✅ ChromaDB API is responding"
else
    echo "   ❌ ChromaDB API is not responding"
    echo "   💡 Check: curl http://localhost:8000/api/v1/heartbeat"
    exit 1
fi

# Step 4: Start dashboard server
echo ""
echo "4️⃣ Starting dashboard server with CORS proxy..."
if check_port 3001; then
    echo "   ⚠️ Port 3001 is already in use"
    echo "   💡 Dashboard might already be running at: http://localhost:3001/chromadb-dashboard.html"
else
    echo "   🔄 Starting dashboard server with proxy..."
    python deployment/dashboard/serve-dashboard-with-proxy.py &
    DASHBOARD_PID=$!
    sleep 2
    
    if check_port 3001; then
        echo "   ✅ Dashboard server started (PID: $DASHBOARD_PID)"
    else
        echo "   ❌ Failed to start dashboard server"
        exit 1
    fi
fi

# Step 5: Open dashboard
echo ""
echo "5️⃣ Opening dashboard..."
if command -v open >/dev/null 2>&1; then
    open http://localhost:3001/chromadb-dashboard.html
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3001/chromadb-dashboard.html
else
    echo "   💡 Manually open: http://localhost:3001/chromadb-dashboard.html"
fi

echo ""
echo "🎉 ChromaDB is ready!"
echo "=================================="
echo "🌐 Dashboard:     http://localhost:3001/chromadb-dashboard.html"
echo "📚 API Docs:      http://localhost:8000/docs"
echo "❤️ Health Check:  http://localhost:8000/api/v1/heartbeat"
echo "📊 Collections:   http://localhost:8000/api/v1/collections"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo ""; echo "👋 Stopping services..."; kill $PORT_FORWARD_PID $DASHBOARD_PID 2>/dev/null; exit 0' INT

# Keep script running
while true; do
    sleep 1
done
