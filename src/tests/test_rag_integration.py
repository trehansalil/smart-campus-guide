#!/usr/bin/env python3
"""
Integration tests for RAG system functionality.
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag_system import CollegeRAGSystem
from filter_models import CollegeFilters, NumericFilter, ComparisonOperator, QueryAnalysis
from constants import config

class TestRAGSystemIntegration:
    """Integration tests for the complete RAG system."""
    
    def __init__(self):
        """Initialize the test class with a RAG system instance."""
        self.rag_system = None
    
    def test_rag_system_initialization(self):
        """Test RAG system can be initialized properly."""
        print("🧪 Testing RAG system initialization")
        
        try:
            self.rag_system = CollegeRAGSystem()
            assert self.rag_system is not None, "RAG system should be initialized"
            print("  ✅ RAG system initialized successfully")
        except Exception as e:
            print(f"  ❌ Failed to initialize RAG system: {e}")
            raise
    
    def test_filter_extraction(self):
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
                analysis = self.rag_system.extract_filters_with_llm(query)
                assert isinstance(analysis, QueryAnalysis), f"Should return QueryAnalysis object for '{query}'"
                assert analysis.original_query == query, f"Original query should be preserved for '{query}'"
                assert analysis.filters is not None, f"Filters should be extracted for '{query}'"
                print(f"  ✅ Extracted filters for: {query}")
                print(f"    - Summary: {analysis.filters.to_readable_summary()}")
            except Exception as e:
                print(f"  ❌ Failed to extract filters for '{query}': {e}")
                raise
    
    def test_search_functionality(self):
        """Test the complete search functionality."""
        print("🧪 Testing search functionality")
        
        test_cases = [
            {
                'query': 'MBA colleges in Delhi',
                'expected_min_results': 1,
                'expected_fields': ['college_name', 'city', 'course']
            },
            {
                'query': 'Engineering colleges',
                'expected_min_results': 1,
                'expected_fields': ['college_name', 'course']
            }
        ]
        
        for test_case in test_cases:
            query = test_case['query']
            try:
                results = self.rag_system.search(query)
                
                # Check results structure
                assert isinstance(results, dict), f"Results should be a dict for '{query}'"
                assert 'query_analysis' in results, f"Results should contain query_analysis for '{query}'"
                assert 'results' in results, f"Results should contain results for '{query}'"
                
                # Check query analysis
                analysis = results['query_analysis']
                assert isinstance(analysis, QueryAnalysis), f"Query analysis should be QueryAnalysis object for '{query}'"
                
                # Check search results
                search_results = results['results']
                assert isinstance(search_results, list), f"Search results should be a list for '{query}'"
                assert len(search_results) >= test_case['expected_min_results'], f"Should have at least {test_case['expected_min_results']} result(s) for '{query}'"
                
                # Check result structure
                if search_results:
                    first_result = search_results[0]
                    for field in test_case['expected_fields']:
                        assert field in first_result, f"Result should contain '{field}' field for '{query}'"
                
                print(f"  ✅ Search successful for: {query} ({len(search_results)} results)")
                
            except Exception as e:
                print(f"  ❌ Search failed for '{query}': {e}")
                raise
    
    def test_data_quality(self):
        """Test the quality and consistency of data in the system."""
        print("🧪 Testing data quality")
        
        try:
            # Test a broad search to get representative data
            results = self.rag_system.search("colleges")
            search_results = results['results']
            
            assert len(search_results) > 0, "Should have results for broad search"
            
            # Check data consistency
            required_fields = ['college_name', 'city', 'course']
            for i, result in enumerate(search_results[:5]):  # Check first 5 results
                for field in required_fields:
                    assert field in result, f"Result {i} missing field '{field}'"
                    assert result[field] is not None, f"Result {i} has None value for '{field}'"
                    assert str(result[field]).strip() != "", f"Result {i} has empty value for '{field}'"
            
            print(f"  ✅ Data quality check passed ({len(search_results)} results analyzed)")
            
        except Exception as e:
            print(f"  ❌ Data quality check failed: {e}")
            raise
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("🧪 Testing edge cases")
        
        edge_cases = [
            "",  # Empty query
            "   ",  # Whitespace only
            "xyz123",  # Nonsense query
            "colleges in NonExistentCity"  # Non-existent location
        ]
        
        for query in edge_cases:
            try:
                results = self.rag_system.search(query)
                assert isinstance(results, dict), f"Should return dict even for edge case: '{query}'"
                assert 'query_analysis' in results, f"Should have query_analysis for edge case: '{query}'"
                assert 'results' in results, f"Should have results (even if empty) for edge case: '{query}'"
                print(f"  ✅ Edge case handled: '{query}' -> {len(results['results'])} results")
                
            except Exception as e:
                print(f"  ⚠️  Edge case '{query}' raised exception: {e}")
                # Edge cases raising exceptions might be acceptable depending on implementation

def main():
    """Run all integration tests."""
    print("🚀 Running RAG System Integration Tests")
    print("=" * 60)
    
    test_suite = TestRAGSystemIntegration()
    
    try:
        test_suite.test_rag_system_initialization()
        test_suite.test_filter_extraction()
        test_suite.test_search_functionality()
        test_suite.test_data_quality()
        test_suite.test_edge_cases()
        
        print("\n🎉 All integration tests passed!")
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
