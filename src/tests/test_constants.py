"""
Unit tests for constants configuration.
"""
import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from constants import config


class TestConstants:
    """Test cases for configuration constants."""
    
    def test_required_env_vars_validation(self):
        """Test that required environment variables are properly validated."""
        missing_vars = config.validate_required_env_vars()
        assert isinstance(missing_vars, list), "validate_required_env_vars should return a list"
        
        # If no missing vars, the list should be empty
        if not missing_vars:
            assert len(missing_vars) == 0
    
    def test_chromadb_url_generation(self):
        """Test ChromaDB URL generation."""
        url = config.get_chromadb_url()
        assert isinstance(url, str), "ChromaDB URL should be a string"
        assert url.startswith('http'), "ChromaDB URL should start with http"
    
    def test_config_attributes(self):
        """Test that essential config attributes exist."""
        essential_attrs = [
            'CHROMA_HOST',
            'CHROMA_PORT', 
            'CHROMA_COLLECTION_NAME',
            'RAG_K',
            'RAG_SCORE_THRESHOLD',
            'EMBEDDING_MODEL_NAME'
        ]
        
        for attr in essential_attrs:
            assert hasattr(config, attr), f"Config should have {attr} attribute"
            value = getattr(config, attr)
            assert value is not None, f"Config.{attr} should not be None"
    
    def test_numeric_configs(self):
        """Test that numeric configurations have correct types."""
        assert isinstance(config.RAG_K, int), "RAG_K should be an integer"
        assert config.RAG_K > 0, "RAG_K should be positive"
        
        assert isinstance(config.RAG_SCORE_THRESHOLD, float), "RAG_SCORE_THRESHOLD should be a float"
        assert 0 <= config.RAG_SCORE_THRESHOLD <= 1, "RAG_SCORE_THRESHOLD should be between 0 and 1"
        
        assert isinstance(config.CHROMA_PORT, int), "CHROMA_PORT should be an integer"
        assert 1 <= config.CHROMA_PORT <= 65535, "CHROMA_PORT should be a valid port number"


if __name__ == "__main__":
    pytest.main([__file__])
