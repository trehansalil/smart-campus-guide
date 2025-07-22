"""
Unit tests for Pydantic filter models.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from filter_models import CollegeFilters, QueryAnalysis, NumericFilter, ComparisonOperator


class TestPydanticModels:
    """Test cases for Pydantic filter models."""
    
    def test_numeric_filter(self):
        """Test NumericFilter functionality."""
        print("🧪 Testing NumericFilter")
        
        # Test fees filter
        fees_filter = NumericFilter(value=1000000, operator=ComparisonOperator.LESS_THAN)
        assert fees_filter.value == 1000000
        assert fees_filter.operator == ComparisonOperator.LESS_THAN
        
        # Test ChromaDB conversion
        chromadb_format = fees_filter.to_chromadb_filter()
        expected = {'$lt': 1000000}
        assert chromadb_format == expected, f"Expected {expected}, got {chromadb_format}"
        print("✅ NumericFilter test passed")
    
    def test_college_filters(self):
        """Test CollegeFilters functionality."""
        print("🧪 Testing CollegeFilters")
        
        # Create test filters
        fees_filter = NumericFilter(value=1000000, operator=ComparisonOperator.LESS_THAN)
        filters = CollegeFilters(
            city="Delhi",
            state=None,
            course="MBA", 
            fees=fees_filter,
            avg_package=None,
            ranking=None,
            college_type="private",
            exam=None
        )
        
        # Test ChromaDB conversion
        chromadb_filters = filters.to_chromadb_filters()
        expected_keys = {'city', 'course', 'fees', 'type'}
        actual_keys = set(chromadb_filters.keys())
        assert expected_keys.issubset(actual_keys), f"Missing keys in ChromaDB filters: {expected_keys - actual_keys}"
        
        # Test specific values
        assert chromadb_filters['city'] == "Delhi"
        assert chromadb_filters['course'] == "MBA"
        assert chromadb_filters['type'] == "private"
        assert chromadb_filters['fees'] == {'$lt': 1000000}
        
        print("✅ CollegeFilters test passed")
    
    def test_readable_summary(self):
        """Test readable summary generation."""
        print("🧪 Testing readable summary")
        
        fees_filter = NumericFilter(value=1000000, operator=ComparisonOperator.LESS_THAN)
        filters = CollegeFilters(
            city="Delhi",
            state=None,
            course="MBA",
            fees=fees_filter,
            avg_package=None,
            ranking=None,
            college_type="private",
            exam=None
        )
        
        summary = filters.to_readable_summary()
        
        # Check that key information is in the summary
        assert "Delhi" in summary
        assert "MBA" in summary
        assert "private" in summary
        assert "10.0L" in summary or "1000000" in summary
        
        print(f"✅ Readable summary: {summary}")
    
    def test_query_analysis(self):
        """Test QueryAnalysis functionality."""
        print("🧪 Testing QueryAnalysis")
        
        fees_filter = NumericFilter(value=1000000, operator=ComparisonOperator.LESS_THAN)
        filters = CollegeFilters(
            city="Delhi",
            state=None,
            course="MBA",
            fees=fees_filter,
            avg_package=None,
            ranking=None,
            college_type="private",
            exam=None
        )
        
        analysis = QueryAnalysis(
            original_query="Best MBA colleges in Delhi under 10 lakhs",
            filters=filters,
            cleaned_query="best colleges",
            intent="find_colleges",
            confidence=0.9
        )
        
        assert analysis.original_query == "Best MBA colleges in Delhi under 10 lakhs"
        assert analysis.cleaned_query == "best colleges"
        assert analysis.intent == "find_colleges"
        assert analysis.confidence == 0.9
        
        # Test search terms
        search_terms = analysis.get_search_terms()
        assert search_terms == "best colleges"
        
        print("✅ QueryAnalysis test passed")


def run_tests():
    """Run all tests."""
    print("🚀 Running Pydantic Models Tests")
    print("=" * 50)
    
    test_class = TestPydanticModels()
    
    try:
        test_class.test_numeric_filter()
        test_class.test_college_filters()
        test_class.test_readable_summary()
        test_class.test_query_analysis()
        
        print("\n🎉 All tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
