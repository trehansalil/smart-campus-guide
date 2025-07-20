#!/bin/bash

# Smart Campus Guide - ChromaDB Deployment Master Script
# This script orchestrates the complete ChromaDB deployment

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"

echo "🚀 Smart Campus Guide - ChromaDB Deployment"
echo "============================================="
echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Deployment dir: $DEPLOYMENT_DIR"
echo ""

# Function to display help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy      Deploy ChromaDB to Kubernetes"
    echo "  start       Start port forwarding and dashboard"
    echo "  stop        Stop all services"
    echo "  test        Test ChromaDB connectivity"
    echo "  dashboard   Start only the dashboard"
    echo "  status      Show deployment status"
    echo "  clean       Remove ChromaDB deployment"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy     # Deploy everything"
    echo "  $0 start      # Start services (after deploy)"
    echo "  $0 test       # Test connectivity"
    echo ""
}

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not found. Please install kubectl to proceed."
        exit 1
    fi
}

# Function to deploy ChromaDB
deploy_chromadb() {
    echo "🚀 Deploying ChromaDB to Kubernetes..."
    check_kubectl
    
    echo "   📝 Applying ChromaDB configuration..."
    kubectl apply -f "$DEPLOYMENT_DIR/kubernetes/chromadb.yaml"
    
    echo "   ⏳ Waiting for ChromaDB pod to be ready..."
    kubectl wait --for=condition=ready pod -l app=chromadb --timeout=300s
    
    echo "   ✅ ChromaDB deployed successfully!"
    echo ""
    echo "   📊 Status:"
    kubectl get pods -l app=chromadb
    kubectl get services -l app=chromadb
    kubectl get pvc chromadb-pvc
}

# Function to start services
start_services() {
    echo "🔄 Starting ChromaDB services..."
    cd "$PROJECT_ROOT"
    exec "$DEPLOYMENT_DIR/scripts/start-chromadb-complete.sh"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping ChromaDB services..."
    
    # Kill port forwarding
    pkill -f "kubectl port-forward.*chromadb" || true
    
    # Kill dashboard servers
    pkill -f "serve-dashboard-with-proxy.py" || true
    pkill -f "serve-dashboard.py" || true
    
    echo "   ✅ Services stopped"
}

# Function to test connectivity
test_connectivity() {
    echo "🧪 Testing ChromaDB connectivity..."
    cd "$PROJECT_ROOT"
    python "$DEPLOYMENT_DIR/scripts/test_chromadb.py"
}

# Function to start only dashboard
start_dashboard() {
    echo "📊 Starting ChromaDB dashboard..."
    cd "$PROJECT_ROOT"
    python "$DEPLOYMENT_DIR/dashboard/serve-dashboard-with-proxy.py"
}

# Function to show status
show_status() {
    echo "📊 ChromaDB Deployment Status"
    echo "============================="
    
    check_kubectl
    
    echo ""
    echo "🏗️ Kubernetes Resources:"
    echo "Pods:"
    kubectl get pods -l app=chromadb 2>/dev/null || echo "   No ChromaDB pods found"
    
    echo ""
    echo "Services:"
    kubectl get services -l app=chromadb 2>/dev/null || echo "   No ChromaDB services found"
    
    echo ""
    echo "PVCs:"
    kubectl get pvc chromadb-pvc 2>/dev/null || echo "   No ChromaDB PVC found"
    
    echo ""
    echo "🌐 Running Services:"
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   ✅ Port 8000 (ChromaDB API) - Active"
    else
        echo "   ❌ Port 8000 (ChromaDB API) - Inactive"
    fi
    
    if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   ✅ Port 3001 (Dashboard) - Active"
    else
        echo "   ❌ Port 3001 (Dashboard) - Inactive"
    fi
}

# Function to clean deployment
clean_deployment() {
    echo "🧹 Cleaning ChromaDB deployment..."
    
    read -p "Are you sure you want to delete ChromaDB deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Cancelled"
        exit 0
    fi
    
    check_kubectl
    
    echo "   🛑 Stopping services..."
    stop_services
    
    echo "   🗑️ Deleting Kubernetes resources..."
    kubectl delete -f "$DEPLOYMENT_DIR/kubernetes/chromadb.yaml" || true
    
    echo "   ✅ Cleanup completed"
}

# Main command processing
case "${1:-help}" in
    deploy)
        deploy_chromadb
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    test)
        test_connectivity
        ;;
    dashboard)
        start_dashboard
        ;;
    status)
        show_status
        ;;
    clean)
        clean_deployment
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
