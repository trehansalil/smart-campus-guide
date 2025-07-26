#!/usr/bin/env python3
"""
Test script to validate state and region extraction in the RAG system.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag.rag_system import extract_filters_with_llm

async def test_state_region_extraction():
    """Test state and region filter extraction from various queries."""
    
    test_queries = [
        # State-based queries
        "MBA colleges in Maharashtra",
        "Engineering colleges in Tamil Nadu", 
        "Best colleges in Karnataka",
        "Private colleges in West Bengal",
        "Government colleges in Gujarat",
        
        # Region-based queries
        "MBA colleges in South India",
        "Engineering colleges in North India",
        "Colleges in West India",
        "Best institutions in East India",
        
        # Mixed queries
        "MBA colleges in Maharashtra under 10 lakhs",
        "Engineering colleges in South India with good placement",
        "Private medical colleges in Tamil Nadu",
        "Government colleges in North India with low fees",
        
        # Variations and typos
        "Colleges in Maharastra",  # Common typo
        "MBA in Tamilnadu",
        "Engineering in south india",
        "colleges in WEST BENGAL",
    ]
    
    print("🧪 Testing State and Region Filter Extraction")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 40)
        
        try:
            analysis = await extract_filters_with_llm(query)
            
            # Show extracted filters
            print(f"✅ Extraction successful (confidence: {analysis.confidence:.1%})")
            print(f"   State: {analysis.filters.state}")
            print(f"   Region: {analysis.filters.region}")
            print(f"   City: {analysis.filters.city}")
            print(f"   Course: {analysis.filters.course}")
            print(f"   College Type: {analysis.filters.college_type}")
            
            # Show city mapping result
            filtered_cities = analysis.filters.get_filtered_cities()
            if filtered_cities:
                print(f"   🌍 Maps to cities: {', '.join(filtered_cities)}")
            
            # Show ChromaDB filter format
            chromadb_filters = analysis.filters.to_chromadb_filters()
            if chromadb_filters:
                print(f"   🔧 ChromaDB filter: {chromadb_filters}")
            
            # Show readable summary
            readable = analysis.filters.to_readable_summary()
            print(f"   📋 Summary: {readable}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_state_region_extraction())
