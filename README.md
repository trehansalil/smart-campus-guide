# Smart Campus Guide 🚀

**Smart Campus Guide** is an AI-powered, Retrieval Augmented Generation (RAG) based college recommendation system that uses vector search, LLMs, and FastAPI to help students make smarter academic choices.

## ✨ Features
- **Vector semantic search** over college databases
- **RAG pipeline** with similarity-based retrieval and prompt-based generation
- **FastAPI** backend with OpenAPI docs
- **Metadata filters, scoring, and JSON API**
- **CLI and Docker support**

## ⚡ Quick Start

### 1. Using [uv](https://github.com/astral-sh/uv) for Dependency Management
```bash
uv venv
. .venv/bin/activate # Windows: .venv\Scripts\activate
uv install
```


### 2. Configure keys
Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run the API

```bash
uv run main:app --reload
```


## 📦 Project Structure
```plaintext
smart-campus-guide/
├── main.py                 # FastAPI app (to be implemented)
├── deployment/             # ChromaDB deployment files
│   ├── kubernetes/         # Kubernetes manifests
│   ├── scripts/           # Deployment scripts
│   ├── dashboard/         # Web dashboard
│   └── README.md          # Deployment guide
├── chromadb.sh            # Master deployment script
├── pyproject.toml         # Dependencies
├── setup.py               # Packaging
└── README.md              # This file
```

## 🚀 ChromaDB Vector Database

This project uses ChromaDB as the vector database for the RAG system. The database is deployed on Kubernetes with a web management interface.

### Quick ChromaDB Setup

```bash
# Deploy ChromaDB to Kubernetes
./chromadb.sh deploy

# Start all services (port forwarding + dashboard)
./chromadb.sh start

# Access the dashboard
open http://localhost:3001/chromadb-dashboard.html
```

For detailed ChromaDB deployment instructions, see [`deployment/README.md`](deployment/README.md).


## 📚 Example Query (API)
```bash
POST /recommend
{
"query": "Best MBA colleges in Bangalore under 5 lakhs fees"
}
```


## 📝 License
MIT
