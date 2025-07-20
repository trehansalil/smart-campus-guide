"""
Test script for the constants configuration.
This script validates that all constants are properly loaded and accessible.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from constants import config, Config


def test_constants():
    """Test the constants configuration."""
    print("=== Testing Constants Configuration ===\n")
    
    # Test 1: Check if config is an instance of Config
    print("1️⃣ Testing config instance...")
    assert isinstance(config, Config), "config should be an instance of Config class"
    print("✅ Config instance test passed")
    
    # Test 2: Check default values
    print("\n2️⃣ Testing default values...")
    assert config.CHROMA_HOST == "localhost", f"Expected localhost, got {config.CHROMA_HOST}"
    assert config.CHROMA_PORT == 8000, f"Expected 8000, got {config.CHROMA_PORT}"
    assert config.RAG_K == 3, f"Expected 3, got {config.RAG_K}"
    assert config.EMBEDDING_MODEL_NAME == "all-MiniLM-L6-v2", f"Expected all-MiniLM-L6-v2, got {config.EMBEDDING_MODEL_NAME}"
    print("✅ Default values test passed")
    
    # Test 3: Check ChromaDB URL generation
    print("\n3️⃣ Testing ChromaDB URL generation...")
    expected_url = "http://localhost:8000"
    actual_url = config.get_chromadb_url()
    assert actual_url == expected_url, f"Expected {expected_url}, got {actual_url}"
    print(f"✅ ChromaDB URL test passed: {actual_url}")
    
    # Test 4: Check validation function
    print("\n4️⃣ Testing validation function...")
    missing_vars = config.validate_required_env_vars()
    print(f"Missing variables: {missing_vars}")
    # At minimum, OPENAI_RAG_MODEL_API_KEY should be missing in test environment
    assert len(missing_vars) >= 1, "Should have at least one missing variable (API key)"
    print("✅ Validation function test passed")
    
    # Test 5: Test environment variable override
    print("\n5️⃣ Testing environment variable override...")
    old_k_value = os.environ.get("RAG_K")
    os.environ["RAG_K"] = "10"
    
    # Create a new config instance to test override
    new_config = Config()
    assert new_config.RAG_K == 10, f"Expected 10, got {new_config.RAG_K}"
    
    # Restore original value
    if old_k_value is None:
        os.environ.pop("RAG_K", None)
    else:
        os.environ["RAG_K"] = old_k_value
    print("✅ Environment variable override test passed")
    
    # Test 6: Print configuration (visual test)
    print("\n6️⃣ Testing configuration printing...")
    config.print_config()
    print("✅ Configuration printing test passed")
    
    print("\n🎉 All tests passed! Constants configuration is working correctly.")


if __name__ == "__main__":
    test_constants()
