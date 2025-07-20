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
├── main.py # FastAPI app
├── rag_system.py # Core RAG logic
├── cli.py # CLI interface
├── colleges_dataset.csv # Data
├── requirements.txt # Dependencies
├── setup.py # Packaging
├── README.md # This file
```


## 📚 Example Query (API)
```bash
POST /recommend
{
"query": "Best MBA colleges in Bangalore under 5 lakhs fees"
}
```


## 📝 License
MIT
