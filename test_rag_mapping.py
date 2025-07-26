#!/usr/bin/env python3
"""
Test script to verify the state and region to city mapping functionality.
"""

import asyncio
import json
from src.rag.simplified_rag import SimplifiedCollegeRAGSystem
from src.rag.filter_models import CollegeFilters, NumericFilter, ComparisonOperator

def test_rag_with_mapping():
    """Test the RAG system with state and region mapping"""
    
    # Initialize RAG system
    rag = SimplifiedCollegeRAGSystem()
    
    print("=== Testing RAG System with Enhanced Mapping ===\n")
    
    # Test 1: State-based query
    print("1. Testing State-based Query:")
    print("Query: 'MBA colleges in Maharashtra'")
    
    filters = CollegeFilters(state="Maharashtra", course="MBA")
    chromadb_filter = filters.to_chromadb_filters()
    print(f"Generated ChromaDB filter: {json.dumps(chromadb_filter, indent=2)}")
    print(f"Cities mapped: {filters.get_filtered_cities()}")
    print(f"Readable summary: {filters.to_readable_summary()}")
    print()
    
    # Test 2: Region-based query
    print("2. Testing Region-based Query:")
    print("Query: 'Engineering colleges in South India'")
    
    filters = CollegeFilters(region="South", course="Engineering")
    chromadb_filter = filters.to_chromadb_filters()
    print(f"Generated ChromaDB filter: {json.dumps(chromadb_filter, indent=2)}")
    print(f"Cities mapped: {filters.get_filtered_cities()}")
    print(f"Readable summary: {filters.to_readable_summary()}")
    print()
    
    # Test 3: Priority handling
    print("3. Testing Priority Handling:")
    print("Query: 'Best colleges in Mumbai, Maharashtra for MBA'")
    
    filters = CollegeFilters(city="Mumbai", state="Maharashtra", course="MBA")
    chromadb_filter = filters.to_chromadb_filters()
    print(f"Generated ChromaDB filter: {json.dumps(chromadb_filter, indent=2)}")
    print(f"Cities mapped: {filters.get_filtered_cities()}")
    print(f"Readable summary: {filters.to_readable_summary()}")
    print()
    
    # Test 4: Complex combination
    print("4. Testing Complex Filter Combination:")
    print("Query: 'Private engineering colleges in West India under 5L fees'")
    
    from src.rag.filter_models import NumericFilter, ComparisonOperator
    
    filters = CollegeFilters(
        region="West",
        course="Engineering", 
        college_type="private",
        fees=NumericFilter(value=500000, operator=ComparisonOperator.LESS_THAN)
    )
    chromadb_filter = filters.to_chromadb_filters()
    print(f"Generated ChromaDB filter: {json.dumps(chromadb_filter, indent=2)}")
    print(f"Cities mapped: {filters.get_filtered_cities()}")
    print(f"Readable summary: {filters.to_readable_summary()}")
    print()

if __name__ == "__main__":
    test_rag_with_mapping()
    print("Testing completed successfully!")
