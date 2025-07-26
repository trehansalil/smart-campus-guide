# Smart Campus Guide 🚀

**Smart Campus Guide** is an AI-powered, Retrieval Augmented Generation (RAG) based college recommendation system that uses vector search, LLMs, and FastAPI to help students make smarter academic choices.

## ✨ Features

- **🔍 Smart Query Processing**: Natural language understanding with LLM-powered filter extraction
- **🎯 Vector Semantic Search**: ChromaDB-powered similarity search over college databases
- **🤖 RAG Pipeline**: Retrieval Augmented Generation with similarity-based retrieval and prompt-based generation
- **⚡ FastAPI Backend**: High-performance REST API with automatic OpenAPI documentation
- **🏷️ Intelligent Filtering**: Metadata filters for fees, location, course type, rankings, and more
- **📊 Scoring & Ranking**: Relevance-based result ordering
- **🐳 Docker & Kubernetes**: Production-ready deployment with ChromaDB clustering
- **🌐 Web Dashboard**: Visual interface for database management

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management (recommended)
- OpenAI API key
- Optional: Docker & Kubernetes for production deployment

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/trehansalil/smart-campus-guide.git
cd smart-campus-guide

# Create virtual environment using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv install
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Required: OpenAI Configuration
OPENAI_RAG_MODEL_API_KEY=your_openai_api_key_here
OPENAI_RAG_MODEL=gpt-4o  # or gpt-4o for cost efficiency

# Optional: Advanced Configuration
CHROMA_PERSIST_DIRECTORY=/path/to/chromadb/storage
CHROMA_COLLECTION_NAME=colleges_rag
RAG_K=5  # Number of results to retrieve
RAG_SCORE_THRESHOLD=0.2  # Minimum similarity score
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2  # Sentence transformer model
```

### 3. Prepare College Data

Ensure you have a `college_dataset.csv` file in the project root with the following columns:
- `name`: College name
- `city`: City location
- `type`: College type (private/govt)
- `course`: Course type (MBA, Engineering, Medicine, etc.)
- `fees`: Annual fees in INR
- `avg_package`: Average placement package in INR
- `ranking`: College ranking (lower is better)
- `exam`: Entrance exam required

### 4. Run the Application

**Option A: Full Stack (FastAPI + Streamlit) - Recommended**
```bash
# Start both backend and frontend
./start_app.sh

# Or start components individually
./start_app.sh api        # Start only FastAPI backend  
./start_app.sh frontend   # Start only Streamlit frontend
./start_app.sh status     # Check service status
./start_app.sh stop       # Stop all services
```

**Option B: Backend Only (FastAPI)**
```bash
# Start the FastAPI server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Alternative: Direct Python execution
python main.py
```

**Option C: Frontend Only (Streamlit)**
```bash
# Start the Streamlit web interface
streamlit run streamlit_app.py
```

The services will be available at:
- **Streamlit Frontend**: http://localhost:8501 (Web UI)
- **FastAPI Backend**: http://localhost:8001 (API)
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🎨 Streamlit Web Interface

The Smart Campus Guide includes a beautiful, user-friendly web interface built with Streamlit:

### 🏠 Features

- **🔍 Intelligent Search**: Natural language college search with real-time recommendations
- **📊 Batch Analysis**: Compare multiple queries simultaneously for better decision making
- **⚙️ System Monitoring**: Real-time health checks and performance metrics
- **📚 Help & Examples**: Comprehensive guides with query templates and best practices
- **🎯 Smart Filtering**: AI-powered understanding of location, budget, and course preferences

### 🚀 Quick Demo

1. **Start the complete system:**
   ```bash
   ./start_app.sh
   ```

2. **Open your browser to http://localhost:8501**

3. **Try example searches:**
   - "MBA colleges in Mumbai under 10 lakhs"
   - "Engineering colleges in Bangalore with good placements"
   - "Private medical colleges with scholarship options"

### 📱 Interface Pages

- **Home**: Quick search, recent queries, and feature overview
- **Search Colleges**: Detailed search with natural language queries
- **Batch Analysis**: Compare multiple search queries side-by-side
- **System Status**: Monitor API health, RAG system status, and performance
- **Help & Examples**: Query templates, best practices, and FAQ
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Sample Queries

### Basic Queries
```bash
# Simple course search
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "MBA colleges in Mumbai"}'

# With budget constraints
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "Engineering colleges under 3 lakhs fees"}'
```

### Advanced Queries with Multiple Filters
```bash
# Complex multi-criteria search
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "Top private MBA colleges in Bangalore with fees under 10 lakhs and good placement packages"}'

# Government college preference
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "Government engineering colleges in Delhi with ranking below 100"}'

# Medical college search
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "Best medical colleges in Chennai for NEET qualified students"}'
```

### Natural Language Examples

The system understands various natural language patterns:

- **"Show me MBA colleges in Mumbai under 5 lakhs"**
- **"Best engineering colleges with good placements"**
- **"Government medical colleges in South India"**
- **"Top private universities for computer science"**
- **"Affordable MBA programs with high ROI"**
- **"Colleges accepting JEE scores in Bangalore"**

## 🏗️ System Architecture & Components

### Core Components

#### 1. **RAG System** (`src/rag/simplified_rag.py`)
The heart of the recommendation engine:

- **Query Analysis**: LLM-powered extraction of structured filters from natural language
- **Vector Search**: ChromaDB semantic similarity search
- **Result Fusion**: Combines filtered and semantic search results
- **Response Generation**: Formats recommendations with relevant metadata

```python
# Example usage
rag_system = SimplifiedCollegeRAGSystem("college_dataset.csv")
await rag_system.initialize()
recommendations = await rag_system.recommend("MBA colleges in Mumbai under 5 lakhs")
```

#### 2. **Filter Models** (`src/rag/filter_models.py`)
Pydantic models for structured data processing:

- **CollegeFilters**: Handles city, course, fees, ranking filters
- **QueryAnalysis**: Structured representation of query intent
- **NumericFilter**: Range-based filtering for fees, packages, rankings

#### 3. **FastAPI Application** (`main.py`)
Production-ready REST API server:

- **Async Architecture**: Non-blocking request handling
- **Error Handling**: Comprehensive error responses
- **CORS Support**: Cross-origin resource sharing
- **Health Checks**: System status monitoring
- **Auto Documentation**: OpenAPI/Swagger integration

#### 4. **Streamlit Frontend** (`streamlit_app.py`)
User-friendly web interface:

- **Intuitive UI**: Clean, modern design with custom styling
- **Real-time Search**: Instant college recommendations
- **Batch Processing**: Compare multiple queries simultaneously
- **System Monitoring**: Live health checks and metrics
- **Interactive Help**: Examples, templates, and best practices
- **Responsive Design**: Works on desktop and mobile devices

#### 5. **Configuration Management** (`src/constants.py`)
Centralized environment variable management:

- **Environment Variables**: Secure API key handling
- **Default Values**: Sensible fallbacks for all settings
- **Validation**: Required variable checking

### Data Flow

```
User Query → LLM Filter Extraction → ChromaDB Vector Search → Result Ranking → Formatted Response
     ↓              ↓                       ↓                    ↓               ↓
"MBA in Mumbai" → {city: Mumbai,      → Semantic similarity   → Score-based   → Structured
                   course: MBA}         + metadata filters      ranking         recommendations
```

## 📦 Project Structure

```plaintext
smart-campus-guide/
├── main.py                          # FastAPI application entry point
├── streamlit_app.py                 # Streamlit web interface
├── start_app.sh                     # Full-stack startup script
├── demo.py                          # System demo and testing script
├── college_dataset.csv              # College data (not included, provide your own)
├── pyproject.toml                   # Python project configuration
├── uv.lock                         # Locked dependencies
├── .env                            # Environment variables (create this)
├── chromadb.sh                     # ChromaDB deployment script
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                 # Streamlit settings
│
├── src/                            # Source code
│   ├── constants.py                # Configuration management
│   ├── api/                        # Enhanced API endpoints
│   │   ├── __init__.py            
│   │   └── enhanced_endpoints.py   # Additional FastAPI endpoints
│   └── rag/                        # RAG system components
│       ├── simplified_rag.py       # Main RAG implementation
│       ├── filter_models.py        # Pydantic data models
│       └── filter_extraction_agent.py  # LLM-based filter extraction
│
├── src/tests/                      # Test suite
│   ├── test_constants.py           # Configuration tests
│   ├── test_pydantic_models.py     # Model validation tests
│   └── test_rag_integration.py     # End-to-end RAG tests
│
├── deployment/                     # Production deployment
│   ├── README.md                   # Deployment guide
│   ├── kubernetes/                 # K8s manifests
│   │   ├── chromadb.yaml          # ChromaDB deployment
│   │   └── chromadb-ingress.yaml  # Ingress configuration
│   ├── scripts/                    # Automation scripts
│   │   ├── start-chromadb-complete.sh
│   │   ├── port-forward-chromadb.sh
│   │   └── test_chromadb.py
│   └── dashboard/                  # Web management interface
│       ├── chromadb-dashboard.html
│       └── serve-dashboard-with-proxy.py
│
├── docs/                           # Documentation
│   ├── CONSTANTS_IMPLEMENTATION_SUMMARY.md
│   ├── ENVIRONMENT_VARIABLES.md
│   ├── README_STREAMLIT.md         # Streamlit documentation
│   └── COMPLETE_GUIDE.md           # Complete setup guide
│
└── config/                         # Configuration files
    └── config.yaml                 # Application settings
```

## 🎯 Usage Examples

### Web Interface (Recommended)
```bash
# Start the complete system
./start_app.sh

# Open browser to http://localhost:8501
# Use the intuitive web interface for searching
```

### API Usage
```bash
# Basic search
curl -X POST "http://localhost:8001/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "MBA colleges in Mumbai under 10 lakhs"}'

# Batch search
curl -X POST "http://localhost:8001/recommend/batch" \
  -H "Content-Type: application/json" \
  -d '["MBA in Delhi", "Engineering in Bangalore"]'
```

### Demo & Testing
```bash
# Run the comprehensive demo
python demo.py

# Check service status
./start_app.sh status
```

## 📊 ChromaDB Vector Database

The system uses ChromaDB as the vector database for storing and querying college embeddings.

### Local Development Setup

```bash
# The system automatically uses local persistent storage
# Data will be stored in ~/.chromadb_autogen by default
python main.py  # ChromaDB will initialize automatically
```

### Production Kubernetes Deployment

```bash
# Deploy ChromaDB cluster to Kubernetes
./chromadb.sh deploy

# Start all services (port forwarding + dashboard)
./chromadb.sh start

# Access the management dashboard
open http://localhost:3001/chromadb-dashboard.html

# Check deployment status
./chromadb.sh status
```

For detailed deployment instructions, see [`deployment/README.md`](deployment/README.md).

## � Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_RAG_MODEL_API_KEY` | *(required)* | OpenAI API key for LLM queries |
| `OPENAI_RAG_MODEL` | `gpt-4o` | OpenAI model for query analysis |
| `CHROMA_PERSIST_DIRECTORY` | `~/.chromadb_autogen` | Local ChromaDB storage path |
| `CHROMA_COLLECTION_NAME` | `colleges_rag` | ChromaDB collection name |
| `RAG_K` | `3` | Number of results to retrieve |
| `RAG_SCORE_THRESHOLD` | `0.2` | Minimum similarity score |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | Sentence transformer model |

### Advanced Configuration

```bash
# High-performance settings
RAG_K=10
RAG_SCORE_THRESHOLD=0.1
RAG_CHUNK_SIZE=2000

# Cost-optimized settings  
OPENAI_RAG_MODEL=gpt-4o
RAG_K=3
RAG_SCORE_THRESHOLD=0.3
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest src/tests/test_constants.py  # Configuration tests
uv run pytest src/tests/test_pydantic_models.py  # Model tests
uv run pytest src/tests/test_rag_integration.py  # Integration tests

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Docker)
```bash
# Build image
docker build -t smart-campus-guide .

# Run container
docker run -p 8000:8000 --env-file .env smart-campus-guide
```

### Kubernetes
```bash
# Deploy full stack
./chromadb.sh deploy
kubectl apply -f deployment/kubernetes/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: Check the `docs/` directory for detailed guides
- **Issues**: Report bugs on [GitHub Issues](https://github.com/trehansalil/smart-campus-guide/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/trehansalil/smart-campus-guide/discussions)
