# Smart Campus Guide - Complete Setup & Usage Guide

## 🎯 Overview

This guide covers the complete setup and usage of the Smart Campus Guide system, including both the FastAPI backend and Streamlit frontend.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │    ChromaDB     │
│   Frontend      │────│    Backend      │────│   Vector DB     │
│  (Port 8501)    │    │  (Port 8001)    │    │  (Port 8000)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
    Web Browser            OpenAI API            College Dataset
```

## 🚀 Quick Start (Complete Stack)

### 1. Prerequisites

- **Python 3.10+** installed
- **OpenAI API Key** (required)
- **College dataset CSV** file
- **Optional**: Docker, Kubernetes for ChromaDB deployment

### 2. Installation

```bash
# Clone repository
git clone https://github.com/trehansalil/smart-campus-guide.git
cd smart-campus-guide

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# OR using uv (recommended)
uv install
```

### 3. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
vim .env  # or nano .env
```

**Required variables in .env:**
```bash
# OpenAI Configuration (REQUIRED)
OPENAI_RAG_MODEL_API_KEY=your_openai_api_key_here

# Optional Configuration
OPENAI_RAG_MODEL=gpt-4
CHROMA_PERSIST_DIRECTORY=/path/to/chromadb/storage
RAG_K=5
RAG_SCORE_THRESHOLD=0.2
```

### 4. Start the Complete System

**Option A: Using the startup script (Recommended)**
```bash
# Make script executable
chmod +x start_app.sh

# Start full stack
./start_app.sh

# Or start components individually
./start_app.sh api        # Only FastAPI
./start_app.sh frontend   # Only Streamlit
./start_app.sh status     # Check status
./start_app.sh stop       # Stop all services
```

**Option B: Manual startup**
```bash
# Terminal 1: Start FastAPI backend
python main.py

# Terminal 2: Start Streamlit frontend
streamlit run streamlit_app.py
```

### 5. Access the Application

- **Streamlit App**: http://localhost:8501
- **FastAPI API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🎨 Using the Streamlit Frontend

### Home Page
- Quick search functionality
- Recent searches
- Feature overview
- Getting started guide

### Search Colleges
1. Enter natural language query
2. Click "Get Recommendations"
3. Review detailed results
4. Copy or share results

**Example queries:**
- "MBA colleges in Mumbai under 10 lakhs"
- "Engineering colleges in Bangalore with good placements"
- "Private medical colleges with scholarship options"

### Batch Analysis
1. Add multiple queries using templates
2. Or manually enter custom queries
3. Click "Analyze All Queries"
4. Compare results across searches

### System Status
- Real-time API health monitoring
- RAG system status
- Configuration details
- Performance metrics

### Help & Examples
- Comprehensive query examples
- Best practices
- FAQ section
- Category-based templates

## 🔧 FastAPI Backend Features

### Core Endpoints

#### Recommendations
```bash
# Single recommendation
curl -X POST "http://localhost:8001/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "MBA colleges in Delhi under 10 lakhs"}'

# Batch recommendations
curl -X POST "http://localhost:8001/recommend/batch" \
  -H "Content-Type: application/json" \
  -d '["MBA in Mumbai", "Engineering in Bangalore"]'
```

#### System Information
```bash
# Health check
curl http://localhost:8001/health

# Configuration
curl http://localhost:8001/config

# API root
curl http://localhost:8001/
```

### Enhanced Endpoints (Optional)

If the enhanced endpoints are loaded, additional functionality is available:

```bash
# Query suggestions
curl "http://localhost:8001/api/v1/suggestions"

# Search categories
curl "http://localhost:8001/api/v1/categories"

# System metrics
curl "http://localhost:8001/api/v1/metrics"

# Popular queries
curl "http://localhost:8001/api/v1/popular-queries"

# Validate query
curl "http://localhost:8001/api/v1/validate-query?query=MBA+colleges"
```

## 📊 ChromaDB Vector Database

### Local Setup (Default)
The system automatically uses local persistent storage:
```bash
# Data stored in ~/.chromadb_autogen by default
# No additional setup required
```

### Kubernetes Deployment (Optional)
```bash
# Deploy ChromaDB cluster
./chromadb.sh deploy

# Start services
./chromadb.sh start

# Access dashboard
open http://localhost:3001/chromadb-dashboard.html

# Check status
./chromadb.sh status
```

## 🛠️ Development & Customization

### Adding Custom Queries to Streamlit

```python
# In streamlit_app.py, modify the suggestions list
custom_queries = [
    "Your custom query here",
    "Another specialized search"
]
```

### Extending the API

```python
# Add new endpoints in main.py
@app.get("/custom-endpoint")
async def custom_function():
    return {"message": "Custom functionality"}
```

### Modifying RAG Configuration

```python
# In src/constants.py
class Config:
    def __init__(self):
        self.RAG_K = int(os.getenv("RAG_K", "5"))  # Modify default
        # ... other configurations
```

## 🔍 Query Examples by Category

### Course-Specific Searches
```
"MBA colleges in Mumbai with finance specialization"
"Computer Science engineering colleges in Bangalore"
"Medical colleges in Delhi accepting NEET scores"
"Law colleges in Chennai with constitutional law programs"
```

### Budget-Based Searches
```
"Engineering colleges under 3 lakhs annual fees"
"Private MBA colleges between 5-10 lakhs"
"Affordable government colleges in Maharashtra"
"Premium colleges with scholarship opportunities"
```

### Location-Based Searches
```
"Top colleges in NCR region"
"Engineering colleges in tier-2 cities"
"South Indian colleges for biotechnology"
"Colleges near Mumbai with hostel facilities"
```

### Ranking & Placement Searches
```
"Top 50 engineering colleges in India"
"Business schools with 90%+ placement rate"
"Government colleges with excellent rankings"
"Colleges with highest placement packages"
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   ```bash
   # Check if FastAPI is running
   curl http://localhost:8001/health
   
   # Check logs
   tail -f fastapi.log
   ```

2. **Streamlit Import Errors**
   ```bash
   # Install missing dependencies
   pip install streamlit plotly requests
   
   # Or reinstall all
   pip install -r requirements.txt
   ```

3. **OpenAI API Errors**
   ```bash
   # Verify API key is set
   echo $OPENAI_RAG_MODEL_API_KEY
   
   # Check .env file
   cat .env | grep OPENAI
   ```

4. **ChromaDB Connection Issues**
   ```bash
   # For Kubernetes deployment
   kubectl get pods -l app=chromadb
   kubectl logs -l app=chromadb
   
   # For local storage
   ls -la ~/.chromadb_autogen
   ```

### Debug Mode

Enable detailed logging:
```bash
# FastAPI debug
LOG_LEVEL=DEBUG python main.py

# Streamlit debug
streamlit run streamlit_app.py --logger.level=debug
```

### Performance Issues

1. **Slow API responses:**
   - Reduce `RAG_K` value
   - Increase `RAG_SCORE_THRESHOLD`
   - Check OpenAI API limits

2. **High memory usage:**
   - Restart services periodically
   - Reduce batch query sizes
   - Monitor system metrics

## 🚀 Production Deployment

### Environment Variables for Production
```bash
# Production API settings
OPENAI_RAG_MODEL=gpt-3.5-turbo  # Cost optimization
RAG_K=3                         # Reduce for faster responses
RAG_SCORE_THRESHOLD=0.3         # Higher threshold

# Security settings
FASTAPI_ENV=production
CORS_ORIGINS=https://yourdomain.com
```

### Docker Deployment

```dockerfile
# Dockerfile for complete stack
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001 8501

# Start both services
CMD ["bash", "-c", "python main.py & streamlit run streamlit_app.py --server.address=0.0.0.0"]
```

### Load Balancing

For high traffic, consider:
- Multiple FastAPI instances behind a load balancer
- Redis for session management
- Dedicated ChromaDB cluster
- CDN for static assets

## 📈 Monitoring & Analytics

### Health Monitoring
```bash
# Automated health checks
curl -f http://localhost:8001/health || exit 1
curl -f http://localhost:8501/_stcore/health || exit 1
```

### Performance Metrics
- Response times via `/api/v1/metrics`
- Query success rates
- System resource usage
- User engagement analytics

### Logging
- FastAPI logs: Check `fastapi.log`
- Streamlit logs: Terminal output
- ChromaDB logs: `kubectl logs -l app=chromadb`

## 🔒 Security Considerations

### API Security
- Rate limiting
- API key authentication
- Input validation
- CORS configuration

### Data Protection
- Secure API key storage
- Environment variable encryption
- Database access controls
- SSL/TLS encryption

## 📞 Support & Contributing

### Getting Help
1. Check troubleshooting section
2. Review logs for error messages
3. Verify all dependencies are installed
4. Test individual components

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

---

**Happy searching! 🎓✨**
