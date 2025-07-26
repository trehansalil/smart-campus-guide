#!/bin/bash

# Smart Campus Guide - Quick Deployment Script
# Usage: ./deploy.sh [platform]

set -e

echo "🚀 Smart Campus Guide - Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating template..."
        cat > .env << EOF
# OpenAI Configuration (REQUIRED)
OPENAI_RAG_MODEL_API_KEY=your_openai_api_key_here

# Optional Configuration
OPENAI_RAG_MODEL=gpt-4
RAG_K=3
RAG_SCORE_THRESHOLD=0.3
API_BASE_URL=http://localhost:8001
EOF
        print_warning "Please edit .env file with your API keys before deployment"
        return 1
    fi
    return 0
}

# Deploy to Streamlit Cloud
deploy_streamlit() {
    print_info "Preparing for Streamlit Community Cloud deployment..."
    
    # Check if requirements.txt exists
    if [ ! -f requirements.txt ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_success "Files ready for Streamlit Cloud deployment!"
    print_info "Next steps:"
    echo "1. Push code to GitHub: git add . && git commit -m 'Deploy to Streamlit' && git push"
    echo "2. Visit: https://share.streamlit.io"
    echo "3. Connect your GitHub repository"
    echo "4. Select streamlit_app.py as the main file"
    echo "5. Add your environment variables in the secrets section"
}

# Deploy to Railway
deploy_railway() {
    print_info "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    # Initialize and deploy
    railway login
    railway init
    railway up
    
    print_success "Deployed to Railway!"
    print_info "Don't forget to set environment variables:"
    echo "railway variables set OPENAI_RAG_MODEL_API_KEY=your_key_here"
}

# Deploy to Heroku
deploy_heroku() {
    print_info "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI not found. Please install it first."
        echo "macOS: brew install heroku/brew/heroku"
        echo "Ubuntu: curl https://cli-assets.heroku.com/install.sh | sh"
        exit 1
    fi
    
    # Login and create app
    heroku login
    read -p "Enter your Heroku app name: " app_name
    heroku create $app_name
    
    # Set environment variables
    if check_env; then
        source .env
        heroku config:set OPENAI_RAG_MODEL_API_KEY=$OPENAI_RAG_MODEL_API_KEY -a $app_name
        heroku config:set API_BASE_URL=https://$app_name.herokuapp.com -a $app_name
    fi
    
    # Deploy
    git push heroku main
    
    print_success "Deployed to Heroku!"
    echo "App URL: https://$app_name.herokuapp.com"
}

# Docker deployment
deploy_docker() {
    print_info "Building and running with Docker..."
    
    # Build image
    docker build -t smart-campus-guide .
    
    # Run container
    if check_env; then
        docker run -d \
            --name smart-campus-guide \
            -p 8501:8501 \
            -p 8001:8001 \
            --env-file .env \
            smart-campus-guide
        
        print_success "Docker container running!"
        print_info "Frontend: http://localhost:8501"
        print_info "API: http://localhost:8001"
    else
        print_error "Please configure .env file first"
        exit 1
    fi
}

# Docker Compose deployment
deploy_compose() {
    print_info "Starting with Docker Compose..."
    
    if [ ! -f docker-compose.yml ]; then
        print_error "docker-compose.yml not found!"
        exit 1
    fi
    
    if check_env; then
        docker-compose up -d --build
        print_success "Services started with Docker Compose!"
        print_info "Frontend: http://localhost:8501"
        print_info "API: http://localhost:8001"
        print_info "ChromaDB: http://localhost:8000"
    else
        print_error "Please configure .env file first"
        exit 1
    fi
}

# Main deployment logic
case "$1" in
    "streamlit"|"cloud")
        deploy_streamlit
        ;;
    "railway")
        deploy_railway
        ;;
    "heroku")
        deploy_heroku
        ;;
    "docker")
        deploy_docker
        ;;
    "compose")
        deploy_compose
        ;;
    "")
        echo "Usage: $0 [platform]"
        echo ""
        echo "Available platforms:"
        echo "  streamlit  - Streamlit Community Cloud (free)"
        echo "  railway    - Railway (recommended for full-stack)"
        echo "  heroku     - Heroku"
        echo "  docker     - Local Docker container"
        echo "  compose    - Docker Compose (full stack)"
        echo ""
        echo "Example: $0 railway"
        ;;
    *)
        print_error "Unknown platform: $1"
        exit 1
        ;;
esac
