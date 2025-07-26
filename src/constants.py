"""
Constants and environment variable configuration for Smart Campus Guide.
Centralized place for all environment variables and application constants.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class to manage all environment variables and constants."""
    
    def __init__(self):
        """Initialize configuration by reading environment variables."""
        self._load_config()
    
    def _load_config(self):
        """Load all configuration values from environment variables."""
        # ChromaDB Configuration
        self.CHROMA_PERSIST_DIRECTORY: str = os.getenv(
            "CHROMA_PERSIST_DIRECTORY", 
            os.path.join(str(Path.home()), ".chromadb_autogen")
        )
        self.CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "colleges_rag")
        self.CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
        self.CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
        
        # RAG Configuration
        self.RAG_K: int = int(os.getenv("RAG_K", "3"))  # Top k results for retrieval
        self.RAG_SCORE_THRESHOLD: float = float(os.getenv("RAG_SCORE_THRESHOLD", "0.2"))
        self.RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1500"))
        
        # Embedding Model Configuration
        self.EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        
        # OpenAI Configuration
        self.OPENAI_RAG_MODEL: str = os.getenv("OPENAI_RAG_MODEL", "gpt-4o")
        self.OPENAI_RAG_MODEL_API_BASE: str = os.getenv(
            "OPENAI_RAG_MODEL_API_BASE", 
            "https://api.openai.com/v1"
        )
        self.OPENAI_RAG_MODEL_API_KEY: str = os.getenv("OPENAI_RAG_MODEL_API_KEY", "")
        self.OPENAI_MAX_RETRIES: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
        
        # Data Configuration
        self.DEFAULT_CSV_PATH: str = os.getenv("COLLEGE_CSV_PATH", "college_dataset.csv")
        
        # Application Configuration
        self.APP_NAME: str = "Smart Campus Guide"
        self.APP_VERSION: str = "1.0.0"
        
        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate_required_env_vars(self) -> list[str]:
        """
        Validate that all required environment variables are set.
        Returns a list of missing required variables.
        """
        missing_vars = []
        
        # Check for required OpenAI API key
        if not self.OPENAI_RAG_MODEL_API_KEY or self.OPENAI_RAG_MODEL_API_KEY == "":
            missing_vars.append("OPENAI_RAG_MODEL_API_KEY")
        
        # Check if CSV file exists
        if not os.path.exists(self.DEFAULT_CSV_PATH):
            missing_vars.append(f"CSV file not found at: {self.DEFAULT_CSV_PATH}")
        
        return missing_vars
    
    def get_chromadb_url(self) -> str:
        """Get the full ChromaDB URL."""
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"
    
    def print_config(self) -> None:
        """Print current configuration (excluding sensitive data)."""
        print(f"=== {self.APP_NAME} Configuration ===")
        print(f"ChromaDB Host: {self.CHROMA_HOST}:{self.CHROMA_PORT}")
        print(f"ChromaDB Collection: {self.CHROMA_COLLECTION_NAME}")
        print(f"Persist Directory: {self.CHROMA_PERSIST_DIRECTORY}")
        print(f"RAG K: {self.RAG_K}")
        print(f"RAG Score Threshold: {self.RAG_SCORE_THRESHOLD}")
        print(f"Embedding Model: {self.EMBEDDING_MODEL_NAME}")
        print(f"OpenAI Model: {self.OPENAI_RAG_MODEL}")
        print(f"OpenAI API Base: {self.OPENAI_RAG_MODEL_API_BASE}")
        print(f"CSV Path: {self.DEFAULT_CSV_PATH}")
        print(f"Log Level: {self.LOG_LEVEL}")
        
        # Check for missing variables
        missing = self.validate_required_env_vars()
        if missing:
            print(f"\n⚠️  Missing required environment variables: {missing}")
        else:
            print("\n✅ All required environment variables are set")


# Create a singleton instance for easy import
config = Config()

# Export commonly used constants
__all__ = [
    "Config",
    "config",
]
