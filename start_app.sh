#!/bin/bash

# Smart Campus Guide - Full Stack Startup Script
# This script starts both the FastAPI backend and Streamlit frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to activate virtual environment if it exists
activate_venv() {
    if [[ -f "$PROJECT_DIR/.venv/bin/activate" ]]; then
        echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
        source "$PROJECT_DIR/.venv/bin/activate"
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    elif [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✅ Virtual environment already active: $VIRTUAL_ENV${NC}"
    else
        echo -e "${YELLOW}⚠️  No virtual environment found${NC}"
        echo -e "${YELLOW}   Install dependencies with: pip install -r requirements.txt${NC}"
    fi
}

echo -e "${BLUE}🚀 Smart Campus Guide - Full Stack Startup${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Function to start FastAPI server
start_fastapi() {
    echo -e "${YELLOW}📡 Starting FastAPI server...${NC}"
    
    # Activate virtual environment
    activate_venv
    
    # Check if port 8001 is already in use
    if check_port 8001; then
        echo -e "${YELLOW}⚠️  Port 8001 is already in use${NC}"
        
        # Check if it's our FastAPI server
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ FastAPI server is already running and healthy${NC}"
            echo -e "${GREEN}   API Documentation: http://localhost:8001/docs${NC}"
            echo -e "${GREEN}   Health Check: http://localhost:8001/health${NC}"
        else
            echo -e "${YELLOW}   Port is in use but health check failed${NC}"
            echo -e "${YELLOW}   If you want to restart, kill the existing process first${NC}"
        fi
    else
        echo -e "${GREEN}✅ Port 8001 is available${NC}"
        cd "$PROJECT_DIR"
        
        # Start FastAPI server in background
        echo -e "${BLUE}   Starting FastAPI on http://localhost:8001${NC}"
        nohup python main.py > fastapi.log 2>&1 &
        FASTAPI_PID=$!
        echo $FASTAPI_PID > fastapi.pid
        
        # Wait for server to start and initialize
        echo -e "${BLUE}   Waiting for server initialization...${NC}"
        sleep 5
        
        # Check if server started successfully with health check
        max_attempts=6
        attempt=1
        while [ $attempt -le $max_attempts ]; do
            if check_port 8001; then
                # Port is open, now check if API is responding
                if curl -s http://localhost:8001/health > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ FastAPI server started successfully (PID: $FASTAPI_PID)${NC}"
                    echo -e "${GREEN}   API Documentation: http://localhost:8001/docs${NC}"
                    echo -e "${GREEN}   Health Check: http://localhost:8001/health${NC}"
                    break
                else
                    echo -e "${YELLOW}   Attempt $attempt/$max_attempts: API initializing...${NC}"
                fi
            else
                echo -e "${YELLOW}   Attempt $attempt/$max_attempts: Server starting...${NC}"
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                echo -e "${RED}❌ Failed to start FastAPI server after $max_attempts attempts${NC}"
                echo -e "${RED}   Check fastapi.log for errors${NC}"
                exit 1
            fi
            
            attempt=$((attempt + 1))
            sleep 3
        done
    fi
}

# Function to start Streamlit app
start_streamlit() {
    echo -e "${YELLOW}🎨 Starting Streamlit frontend...${NC}"
    
    # Activate virtual environment
    activate_venv
    
    # Check if port 8501 is already in use
    if check_port 8501; then
        echo -e "${YELLOW}⚠️  Port 8501 is already in use (Streamlit may already be running)${NC}"
        echo -e "${YELLOW}   If you want to restart, kill the existing process first${NC}"
    else
        echo -e "${GREEN}✅ Port 8501 is available${NC}"
        cd "$PROJECT_DIR"
        
        # Start Streamlit app
        echo -e "${BLUE}   Starting Streamlit on http://localhost:8501${NC}"
        
        # Verify streamlit is available
        if ! command -v streamlit &> /dev/null; then
            echo -e "${RED}❌ Streamlit command not found${NC}"
            echo -e "${RED}   Install with: pip install streamlit${NC}"
            exit 1
        fi
        
        # Start Streamlit (this will block)
        streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501 --browser.gatherUsageStats=false
    fi
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "${GREEN}✅ Python version: $python_version${NC}"
    
    # Check if required files exist
    if [[ ! -f "$PROJECT_DIR/main.py" ]]; then
        echo -e "${RED}❌ main.py not found${NC}"
        exit 1
    fi
    
    if [[ ! -f "$PROJECT_DIR/streamlit_app.py" ]]; then
        echo -e "${RED}❌ streamlit_app.py not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Required files found${NC}"
    
    # Check for environment variables
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        echo -e "${GREEN}✅ .env file found${NC}"
    else
        echo -e "${YELLOW}⚠️  .env file not found${NC}"
        echo -e "${YELLOW}   Create one with your OpenAI API key: OPENAI_RAG_MODEL_API_KEY=your_key${NC}"
    fi
    
    # Check if ChromaDB is running (if using external instance)
    echo -e "${BLUE}ℹ️  Checking ChromaDB status...${NC}"
    if command -v kubectl &> /dev/null; then
        if kubectl get pods -l app=chromadb 2>/dev/null | grep -q "Running"; then
            echo -e "${GREEN}✅ ChromaDB pod is running${NC}"
        else
            echo -e "${YELLOW}⚠️  ChromaDB pod not found or not running${NC}"
            echo -e "${YELLOW}   Run: ./chromadb.sh start (if using Kubernetes deployment)${NC}"
        fi
    fi
}

# Function to show status
show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    echo -e "${BLUE}==================${NC}"
    
    # FastAPI status
    if check_port 8001; then
        echo -e "${GREEN}✅ FastAPI Backend: Running on http://localhost:8001${NC}"
        # Try to get health status
        if command -v curl &> /dev/null; then
            health_status=$(curl -s http://localhost:8001/health 2>/dev/null || echo "Connection failed")
            if [[ "$health_status" != "Connection failed" ]]; then
                echo -e "${GREEN}   Health: OK${NC}"
            else
                echo -e "${YELLOW}   Health: Cannot connect${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ FastAPI Backend: Not running${NC}"
    fi
    
    # Streamlit status
    if check_port 8501; then
        echo -e "${GREEN}✅ Streamlit Frontend: Running on http://localhost:8501${NC}"
    else
        echo -e "${RED}❌ Streamlit Frontend: Not running${NC}"
    fi
    
    # ChromaDB status
    if command -v kubectl &> /dev/null; then
        if kubectl get pods -l app=chromadb 2>/dev/null | grep -q "Running"; then
            echo -e "${GREEN}✅ ChromaDB: Running (Kubernetes)${NC}"
        else
            echo -e "${YELLOW}⚠️  ChromaDB: Not detected${NC}"
        fi
    fi
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    
    # Stop FastAPI if PID file exists
    if [[ -f "$PROJECT_DIR/fastapi.pid" ]]; then
        fastapi_pid=$(cat "$PROJECT_DIR/fastapi.pid")
        if ps -p $fastapi_pid > /dev/null 2>&1; then
            echo -e "${YELLOW}   Stopping FastAPI (PID: $fastapi_pid)${NC}"
            kill $fastapi_pid
            rm -f "$PROJECT_DIR/fastapi.pid"
            echo -e "${GREEN}✅ FastAPI stopped${NC}"
        else
            echo -e "${YELLOW}   FastAPI PID not found or already stopped${NC}"
            rm -f "$PROJECT_DIR/fastapi.pid"
        fi
    fi
    
    # Kill any remaining processes on our ports
    if check_port 8001; then
        echo -e "${YELLOW}   Killing process on port 8001${NC}"
        lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    fi
    
    if check_port 8501; then
        echo -e "${YELLOW}   Killing process on port 8501${NC}"
        lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Function to show help
show_help() {
    echo -e "${BLUE}Smart Campus Guide - Startup Script${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [command]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  start       Start both FastAPI and Streamlit (default)"
    echo "  api         Start only FastAPI backend"
    echo "  frontend    Start only Streamlit frontend"
    echo "  status      Show service status"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  help        Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0              # Start full stack"
    echo "  $0 start        # Start full stack"
    echo "  $0 api          # Start only API"
    echo "  $0 frontend     # Start only frontend"
    echo "  $0 status       # Check status"
    echo ""
    echo -e "${YELLOW}URLs:${NC}"
    echo "  Frontend:     http://localhost:8501"
    echo "  API:          http://localhost:8001"
    echo "  API Docs:     http://localhost:8001/docs"
    echo "  Health Check: http://localhost:8001/health"
}

# Handle cleanup on script exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    # Note: We don't auto-stop services on script exit to allow them to continue running
}
trap cleanup EXIT

# Main script logic
case "${1:-start}" in
    "start"|"")
        check_prerequisites
        start_fastapi
        sleep 2
        start_streamlit
        ;;
    "api")
        check_prerequisites
        start_fastapi
        echo -e "${GREEN}✅ FastAPI server is running${NC}"
        echo -e "${BLUE}ℹ️  To start frontend: $0 frontend${NC}"
        ;;
    "frontend")
        # Check if API is running
        if ! check_port 8001; then
            echo -e "${YELLOW}⚠️  FastAPI backend is not running${NC}"
            echo -e "${YELLOW}   Start it with: $0 api${NC}"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
        start_streamlit
        ;;
    "status")
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        check_prerequisites
        start_fastapi
        sleep 2
        start_streamlit
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
