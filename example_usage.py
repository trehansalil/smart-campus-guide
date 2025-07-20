"""
Example script showing how to use the RAG system with environment variables.
Run this script to test the college recommendation system.
"""
import asyncio
import sys
from constants import config
from rag_system import CollegeRAGSystem


async def main():
    """Main function to demonstrate the RAG system usage."""
    print(f"=== {config.APP_NAME} v{config.APP_VERSION} ===")
    
    # Validate configuration
    missing_vars = config.validate_required_env_vars()
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {missing_vars}")
        print("\nPlease set the following environment variables:")
        for var in missing_vars:
            if "OPENAI" in var:
                print(f"export {var}='your_openai_api_key_here'")
            else:
                print(f"export {var}='appropriate_value'")
        sys.exit(1)
    
    # Initialize RAG system
    print("\n🔄 Initializing RAG system...")
    rag = CollegeRAGSystem()
    
    try:
        await rag.initialize()
        print("✅ RAG system initialized successfully!")
        
        # Example queries
        queries = [
            "Best private MBA colleges in Delhi under 10 lakhs fees",
            "Top engineering colleges in Bangalore with good placement",
            "Affordable medical colleges in Tamil Nadu",
            "Best computer science colleges in Mumbai"
        ]
        
        print(f"\n🎯 Running example queries with k={config.RAG_K} results...")
        
        for i, query in enumerate(queries, 1):
            print(f"\n--- Query {i} ---")
            print(f"Q: {query}")
            print("A:", end=" ")
            
            try:
                answer = await rag.recommend(query)
                print(answer)
            except Exception as e:
                print(f"❌ Error processing query: {e}")
            
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        print("\n🧹 Cleaning up resources...")
        await rag.close()
        print("✅ Cleanup completed!")


if __name__ == "__main__":
    # Set some example environment variables if they're not set
    import os
    
    # Only set defaults if not already set in environment
    env_defaults = {
        "RAG_K": "5",
        "RAG_SCORE_THRESHOLD": "0.15",
        "LOG_LEVEL": "INFO",
        "COLLEGE_CSV_PATH": "college_dataset.csv"
    }
    
    for key, value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = value
    
    # Run the example
    asyncio.run(main())
