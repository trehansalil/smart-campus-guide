# Environment Variables Configuration

The Smart Campus Guide RAG system uses environment variables for configuration management. This approach provides flexibility and security for different deployment environments.

## Configuration Files

### `constants.py`
Central configuration management file that loads all environment variables and provides default values.

### `.env.example`
Template file showing all available environment variables with example values.

## Required Environment Variables

### OpenAI Configuration (Required)
- `OPENAI_RAG_MODEL_API_KEY`: Your OpenAI API key (required)
- `OPENAI_RAG_MODEL`: OpenAI model to use (default: "gpt-4")
- `OPENAI_RAG_MODEL_API_BASE`: OpenAI API base URL (default: "https://api.openai.com/v1")
- `OPENAI_MAX_RETRIES`: Maximum retries for API calls (default: 3)

### ChromaDB Configuration
- `CHROMA_HOST`: ChromaDB host (default: "localhost")
- `CHROMA_PORT`: ChromaDB port (default: 8000)
- `CHROMA_COLLECTION_NAME`: Collection name for RAG data (default: "colleges_rag")
- `CHROMA_PERSIST_DIRECTORY`: Directory for persistent storage (default: ~/.chromadb_autogen)

### RAG System Configuration
- `RAG_K`: Number of top results to retrieve (default: 3)
- `RAG_SCORE_THRESHOLD`: Minimum similarity score threshold (default: 0.2)
- `RAG_CHUNK_SIZE`: Text chunk size for indexing (default: 1500)

### Embedding Model Configuration
- `EMBEDDING_MODEL_NAME`: Sentence transformer model (default: "all-MiniLM-L6-v2")

### Data Configuration
- `COLLEGE_CSV_PATH`: Path to the college dataset CSV file (default: "college_dataset.csv")

### Application Configuration
- `LOG_LEVEL`: Logging level (default: "INFO")

## Setup Instructions

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file and set your values:**
   ```bash
   # Required - Set your OpenAI API key
   OPENAI_RAG_MODEL_API_KEY=your_actual_api_key_here
   
   # Optional - Customize other settings as needed
   RAG_K=5
   RAG_SCORE_THRESHOLD=0.15
   ```

3. **Load environment variables (if using .env file):**
   ```bash
   # Option 1: Export variables manually
   export $(cat .env | xargs)
   
   # Option 2: Use python-dotenv in your code
   pip install python-dotenv
   ```

## Usage Examples

### Basic Usage
```python
from src.constants import config
from rag_system import CollegeRAGSystem

# The config automatically loads environment variables
rag = CollegeRAGSystem()
await rag.initialize()
```

### Configuration Validation
```python
from src.constants import config

# Check for missing required variables
missing_vars = config.validate_required_env_vars()
if missing_vars:
    print(f"Missing variables: {missing_vars}")
else:
    print("All required variables are set!")
```

### Print Current Configuration
```python
from src.constants import config

# Print current configuration (excluding sensitive data)
config.print_config()
```

### Dynamic Configuration
```python
import os
from src.constants import config

# Override environment variables at runtime
os.environ["RAG_K"] = "10"
os.environ["RAG_SCORE_THRESHOLD"] = "0.1"

# Create new config instance with updated values
new_config = Config()
print(f"New RAG_K: {new_config.RAG_K}")
```

## Testing

Run the configuration test to verify everything is working:

```bash
python3 test_constants.py
```

This will validate:
- Default values are loaded correctly
- Environment variable overrides work
- ChromaDB URL generation functions
- Required variable validation
- Configuration printing

## Example Scripts

- `example_usage.py`: Complete example showing how to use the RAG system with environment variables
- `test_constants.py`: Test script to validate the constants configuration

## Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure and don't share it
- Use different environment files for development, staging, and production
- Consider using a secrets management system for production deployments
