#!/usr/bin/env python3
"""
Tests for constants.py - Validation of configuration constants
"""
import sys
import os

# Add parent directory to path to import constants
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constants import config

class TestConstants:
    """Test class for constants validation."""
    
    def test_string_constants(self):
        """Test that string constants are defined and not empty."""
        print("🧪 Testing string constants")
        
        string_constants = {
            'CHROMA_PERSIST_DIRECTORY': config.CHROMA_PERSIST_DIRECTORY,
            'CHROMA_COLLECTION_NAME': config.CHROMA_COLLECTION_NAME, 
            'OPENAI_RAG_MODEL': config.OPENAI_RAG_MODEL,
            'EMBEDDING_MODEL_NAME': config.EMBEDDING_MODEL_NAME
        }
        
        for name, value in string_constants.items():
            assert isinstance(value, str), f"{name} should be a string, got {type(value)}"
            assert value.strip() != "", f"{name} should not be empty"
            print(f"  ✅ {name}: {value}")
    
    def test_numeric_constants(self):
        """Test that numeric constants are properly defined."""
        print("🧪 Testing numeric constants")
        
        # Test RAG_K
        assert isinstance(config.RAG_K, int), "RAG_K should be an integer"
        assert config.RAG_K > 0, "RAG_K should be positive"
        print(f"  ✅ RAG_K: {config.RAG_K}")
        
        # Test RAG_SCORE_THRESHOLD
        assert isinstance(config.RAG_SCORE_THRESHOLD, (int, float)), "RAG_SCORE_THRESHOLD should be numeric"
        assert 0 <= config.RAG_SCORE_THRESHOLD <= 1, "RAG_SCORE_THRESHOLD should be between 0 and 1"
        print(f"  ✅ RAG_SCORE_THRESHOLD: {config.RAG_SCORE_THRESHOLD}")
        
        # Test CHROMA_PORT
        assert isinstance(config.CHROMA_PORT, int), "CHROMA_PORT should be an integer"
        assert 1 <= config.CHROMA_PORT <= 65535, "CHROMA_PORT should be a valid port number"
        print(f"  ✅ CHROMA_PORT: {config.CHROMA_PORT}")
    
    def test_validation_method(self):
        """Test the validation method."""
        print("🧪 Testing validation method")
        
        missing_vars = config.validate_required_env_vars()
        assert isinstance(missing_vars, list), "validate_required_env_vars should return a list"
        print(f"  ✅ Missing environment variables: {missing_vars}")
        
        # If there are missing vars, they should be strings
        for var in missing_vars:
            assert isinstance(var, str), f"Missing variable '{var}' should be a string"

def main():
    """Run all tests."""
    print("🚀 Running Constants Tests")
    print("=" * 50)
    
    test_suite = TestConstants()
    
    try:
        test_suite.test_string_constants()
        test_suite.test_numeric_constants() 
        test_suite.test_validation_method()
        
        print("\n🎉 All tests passed!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
