#!/usr/bin/env python3
"""
Integration tests for RAG system functionality.
"""
import sys
import os
import asyncio

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simplified_rag import SimplifiedCollegeRAGSystem, extract_filters_with_llm
from filter_models import QueryAnalysis

class TestRAGSystemIntegration:
    """Integration tests for the complete RAG system."""
    
    def __init__(self):
        """Initialize the test class with a RAG system instance."""
        self.rag_system = None
    
    async def test_rag_system_initialization(self):
        """Test RAG system can be initialized properly."""
        print("🧪 Testing RAG system initialization")
        
        try:
            self.rag_system: SimplifiedCollegeRAGSystem = SimplifiedCollegeRAGSystem()
            await self.rag_system.initialize()
            assert self.rag_system is not None, "RAG system should be initialized"
            print("  ✅ RAG system initialized successfully")
        except Exception as e:
            print(f"  ❌ Failed to initialize RAG system: {e}")
            raise
    
    async def test_filter_extraction(self):
        """Test LLM-powered filter extraction from natural language queries."""
        print("🧪 Testing filter extraction")
        
        test_queries = [
            "MBA colleges in Delhi under 10 lakhs",
            "Engineering colleges in Mumbai",
            "Private medical colleges",
            "Top law colleges with fees under 5 lakhs"
        ]
        
        for query in test_queries:
            try:
                analysis = await extract_filters_with_llm(query)
                assert isinstance(analysis, QueryAnalysis), f"Should return QueryAnalysis object for '{query}'"
                assert analysis.original_query == query, f"Original query should be preserved for '{query}'"
                assert analysis.filters is not None, f"Filters should be extracted for '{query}'"
                print(f"  ✅ Extracted filters for: {query}")
                print(f"    - Summary: {analysis.filters.to_readable_summary()}")
                print(f"    - Confidence: {analysis.confidence:.1%}")
            except Exception as e:
                print(f"  ❌ Failed to extract filters for '{query}': {e}")
                raise
    
    async def test_recommendation_functionality(self):
        """Test the complete recommendation functionality."""
        print("🧪 Testing recommendation functionality")
        
        test_cases = [
            {
                'query': 'MBA colleges in Delhi',
                'expected_keywords': ['MBA', 'Delhi']
            },
            {
                'query': 'Engineering colleges in Mumbai',
                'expected_keywords': ['Engineering', 'Mumbai']
            },
            {
                'query': 'Private colleges under 5 lakhs',
                'expected_keywords': ['Private']
            }
        ]
        
        for test_case in test_cases:
            query = test_case['query']
            try:
                recommendation = await self.rag_system.recommend(query)
                
                # Check that we get a string response
                assert isinstance(recommendation, str), f"Recommendation should be a string for '{query}'"
                assert len(recommendation) > 0, f"Recommendation should not be empty for '{query}'"
                
                # Check that the recommendation is not an error message
                assert not recommendation.startswith("❌"), f"Should not get error for valid query '{query}'"
                
                # Check that some expected keywords appear in the response
                for keyword in test_case['expected_keywords']:
                    assert keyword.lower() in recommendation.lower(), f"Recommendation should mention '{keyword}' for query '{query}'"
                
                print(f"  ✅ Recommendation successful for: {query}")
                print(f"    - Response length: {len(recommendation)} characters")
                
            except Exception as e:
                print(f"  ❌ Recommendation failed for '{query}': {e}")
                raise
    
    async def test_data_quality(self):
        """Test the quality and consistency of recommendations."""
        print("🧪 Testing data quality")
        
        try:
            # Test a broad search to get representative data
            recommendation = await self.rag_system.recommend("best colleges")
            
            assert isinstance(recommendation, str), "Should return string recommendation"
            assert len(recommendation) > 0, "Should have non-empty recommendation"
            assert not recommendation.startswith("❌"), "Should not get error for broad search"
            
            # Check for expected formatting
            assert "**" in recommendation, "Should have formatted college names with **"
            
            print(f"  ✅ Data quality check passed")
            print(f"    - Recommendation preview: {recommendation[:100]}...")
            
        except Exception as e:
            print(f"  ❌ Data quality check failed: {e}")
            raise
    
    async def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("🧪 Testing edge cases")
        
        edge_cases = [
            "xyz123",  # Nonsense query
            "colleges in NonExistentCity",  # Non-existent location
            "MBA colleges with fees over 100 crores"  # Unrealistic criteria
        ]
        
        for query in edge_cases:
            try:
                recommendation = await self.rag_system.recommend(query)
                assert isinstance(recommendation, str), f"Should return string even for edge case: '{query}'"
                print(f"  ✅ Edge case handled: '{query}' -> {len(recommendation)} chars")
                
            except Exception as e:
                print(f"  ⚠️  Edge case '{query}' raised exception: {e}")
                # Some edge cases raising exceptions might be acceptable

async def main():
    """Run all integration tests."""
    print("🚀 Running RAG System Integration Tests")
    print("=" * 60)
    
    test_suite = TestRAGSystemIntegration()
    
    try:
        await test_suite.test_rag_system_initialization()
        await test_suite.test_filter_extraction()
        await test_suite.test_recommendation_functionality()
        await test_suite.test_data_quality()
        await test_suite.test_edge_cases()
        
        # Cleanup
        if test_suite.rag_system:
            await test_suite.rag_system.close()
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
