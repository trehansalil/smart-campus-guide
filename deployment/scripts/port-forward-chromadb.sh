#!/bin/bash

# ChromaDB Port Forward Script
# This script forwards the ChromaDB service to your local machine

echo "🚀 Starting ChromaDB port forwarding..."
echo "📊 ChromaDB UI will be available at: http://localhost:8000"
echo "📚 API Documentation at: http://localhost:8000/docs"
echo "❤️ Health Check at: http://localhost:8000/api/v1/heartbeat"
echo ""
echo "Press Ctrl+C to stop port forwarding"
echo ""

# Forward ChromaDB service port 8000 to local port 8000
kubectl port-forward service/chromadb 8000:8000

echo "👋 Port forwarding stopped"
