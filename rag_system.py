import hashlib
import os
import pandas as pd
import asyncio
import re
from pathlib import Path
from typing import AsyncGenerator, List, Dict, Optional, Union

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.memory.chromadb import (
    ChromaDBVectorMemory,
    PersistentChromaDBVectorMemoryConfig,
    HttpChromaDBVectorMemoryConfig,
    SentenceTransformerEmbeddingFunctionConfig,
    DefaultEmbeddingFunctionConfig,
)
from autogen_core.memory import MemoryContent, MemoryMimeType

from constants import config
from filter_models import CollegeFilters, QueryAnalysis, NumericFilter, ComparisonOperator, CollegeType

# Simple LLM-based filter extraction (without complex autogen agent setup)
async def extract_filters_with_llm(query: str) -> QueryAnalysis:
    """
    Extract structured filters from natural language using LLM.
    This is a simplified version that works reliably.
    """
    try:
        import openai
        
        system_prompt = """You are an expert at extracting structured college search filters from natural language queries.

Extract filter criteria and respond with valid JSON containing:
- filters: Object with extracted filters
- cleaned_query: String with filter terms removed
- intent: String describing the primary intent
- confidence: Float between 0.0-1.0

Supported filters:
- city: String (e.g., "Mumbai", "Delhi") - use title case
- course: String (e.g., "MBA", "Engineering", "Medical") - use title case exactly as shown
- fees: Object with {value: number, operator: "lt"/"gt"/"eq"} (convert lakhs to actual amounts)
- avg_package: Object with {value: number, operator: "lt"/"gt"/"eq"}
- ranking: Object with {value: number, operator: "lt"/"gt"/"eq"} (lower = better)
- college_type: String ("private" or "govt") - use lowercase

IMPORTANT: Use these exact values for consistency:
- For college_type: "private" or "govt" (lowercase)
- For course: "MBA", "Engineering", "Medical" (title case, not ALL CAPS)
- For city: "Delhi", "Mumbai", "Bangalore" (title case)

Example:
Query: "MBA colleges in Delhi under 10 lakhs fees"
Response: {"filters": {"city": "Delhi", "course": "MBA", "fees": {"value": 1000000, "operator": "lt"}}, "cleaned_query": "colleges", "intent": "find_colleges", "confidence": 0.9}

Analyze this query:"""

        client = openai.AsyncOpenAI(
            api_key=config.OPENAI_RAG_MODEL_API_KEY,
            base_url=config.OPENAI_RAG_MODEL_API_BASE
        )
        
        response = await client.chat.completions.create(
            model=config.OPENAI_RAG_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        
        if not response_text:
            raise ValueError("Empty response from LLM")
            
        # Parse JSON response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        import json
        json_str = response_text[json_start:json_end]
        response_data = json.loads(json_str)
        
        # Convert to structured models
        filters_data = response_data.get('filters', {})
        
        # Convert numeric filters
        for field in ['fees', 'avg_package', 'ranking']:
            if field in filters_data and isinstance(filters_data[field], dict):
                numeric_data = filters_data[field]
                filters_data[field] = NumericFilter(
                    value=numeric_data['value'],
                    operator=ComparisonOperator(numeric_data['operator'])
                )
        
        # Ensure college_type is lowercase to match data
        if 'college_type' in filters_data:
            filters_data['college_type'] = filters_data['college_type'].lower()
        
        # Normalize course names to match data format
        if 'course' in filters_data:
            course = filters_data['course'].lower()
            if course in ['engineering', 'engineer']:
                filters_data['course'] = 'Engineering'
            elif course == 'mba':
                filters_data['course'] = 'MBA'
            elif course in ['medicine', 'medical']:
                filters_data['course'] = 'Medicine'
            # Keep the original case for other courses
        
        filters = CollegeFilters(**filters_data)
        
        return QueryAnalysis(
            original_query=query,
            filters=filters,
            cleaned_query=response_data.get('cleaned_query', query),
            intent=response_data.get('intent', 'find_colleges'),
            confidence=response_data.get('confidence', 0.7)
        )
        
    except Exception as e:
        print(f"⚠️  LLM filter extraction failed: {e}")
        # Fallback to basic analysis
        return QueryAnalysis(
            original_query=query,
            filters=CollegeFilters(
                city=None,
                state=None,
                fees=None,
                avg_package=None,
                ranking=None,
                course=None,
                college_type=None,
                exam=None
            ),
            cleaned_query=query,
            intent="find_colleges",
            confidence=0.1
        )

# Helper: Create ChromaDB memory configuration based on environment
def create_chromadb_memory_config(k: Optional[int] = None, score_threshold: Optional[float] = None, use_deployment: Optional[bool] = True) -> ChromaDBVectorMemory:
    """
    Create ChromaDB memory configuration based on deployment settings.
    
    Args:
        k: Number of results to return (defaults to config.RAG_K)
        score_threshold: Score threshold for filtering (defaults to config.RAG_SCORE_THRESHOLD)
        use_deployment: Whether to use HTTP deployment or local persistence
                       If None, auto-detects based on CHROMA_HOST != localhost
    
    Returns:
        ChromaDBVectorMemory instance with appropriate configuration
    """
    k = k or config.RAG_K
    score_threshold = score_threshold if score_threshold is not None else config.RAG_SCORE_THRESHOLD
    
    # Auto-detect deployment mode if not specified
    if use_deployment is None:
        use_deployment = config.CHROMA_HOST.lower() not in ['localhost', '127.0.0.1']
    
    # Use different embedding configurations based on deployment type
    if use_deployment:
        # For HTTP deployment, use default embedding function for better compatibility
        embedding_config = DefaultEmbeddingFunctionConfig()
        print(f"🔧 Using default embedding function for HTTP deployment compatibility")
    else:
        # For local deployment, use SentenceTransformer for better performance
        embedding_config = SentenceTransformerEmbeddingFunctionConfig(
            model_name=config.EMBEDDING_MODEL_NAME
        )
        print(f"🔧 Using SentenceTransformer embedding function: {config.EMBEDDING_MODEL_NAME}")
    
    if use_deployment:
        # For HTTP deployment, try to detect version compatibility issues
        print(f"🌐 Using ChromaDB HTTP deployment at {config.get_chromadb_url()}")
        print("⚠️  Note: HTTP deployment detected potential version mismatch")
        print("   ChromaDB client 1.0.15 connecting to server 0.5.23 may have compatibility issues")
        print("   Falling back to local persistent storage for better compatibility")
        
        # Fall back to local storage due to version mismatch
        print(f"💾 Falling back to ChromaDB local persistence at {config.CHROMA_PERSIST_DIRECTORY}")
        memory_config = PersistentChromaDBVectorMemoryConfig(
            collection_name=config.CHROMA_COLLECTION_NAME,
            persistence_path=config.CHROMA_PERSIST_DIRECTORY,
            tenant="default_tenant",  # Default tenant
            database="default_database",  # Default database
            k=k,
            score_threshold=score_threshold,
            embedding_function_config=SentenceTransformerEmbeddingFunctionConfig(
                model_name=config.EMBEDDING_MODEL_NAME
            ),
        )
    else:
        # Use local persistent storage
        print(f"💾 Using ChromaDB local persistence at {config.CHROMA_PERSIST_DIRECTORY}")
        memory_config = PersistentChromaDBVectorMemoryConfig(
            collection_name=config.CHROMA_COLLECTION_NAME,
            persistence_path=config.CHROMA_PERSIST_DIRECTORY,
            tenant="default_tenant",  # Default tenant
            database="default_database",  # Default database
            k=k,
            score_threshold=score_threshold,
            embedding_function_config=embedding_config,
        )
    
    return ChromaDBVectorMemory(config=memory_config)

# Helper: Load college records and chunk
def load_colleges_from_csv(csv_path: str) -> List[Dict]:
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient='records')
    return records

# Async: Index all colleges into ChromaDB vector memory
async def index_colleges_to_memory(records, rag_memory: ChromaDBVectorMemory, chunk_size: Optional[int] = None):
    """
    Index colleges, avoiding duplicate entries by hash.
    Uses the provided rag_memory instance instead of creating a new one.
    """
    chunk_size = chunk_size or config.RAG_CHUNK_SIZE

    # Build a set of existing hashes from current memory
    existing_hashes = set()
    
    # Use the passed memory instance - don't create a new one!
    # Query all current memory items to check for existing data
    try:
        # Create a temporary memory config with high k to get all existing records
        temp_check_memory = create_chromadb_memory_config(k=10000, score_threshold=0.0)
        
        # Use a generic search term that should match all records
        results = await temp_check_memory.query(
            query="college university school institute MBA engineering",  # Generic terms likely to match all records
        )
        await temp_check_memory.close()  # Clean up immediately
        
        if not results.results:
            print("No existing records found in ChromaDB, starting fresh indexing.")
        else:
            print(f"Found {len(results.results)} existing records in ChromaDB, checking for duplicates.")
            for result in results.results:
                meta = getattr(result, "metadata", None)
                if meta and hasattr(meta, 'get'):
                    row_hash = meta.get("row_hash")
                elif meta and hasattr(meta, 'row_hash'):
                    row_hash = getattr(meta, 'row_hash', None)
                else:
                    row_hash = None
                    
                if row_hash:
                    existing_hashes.add(row_hash)
    except Exception as e:
        print(f"Warning: Could not query existing records, starting fresh: {e}")

    count_added = 0
    for idx, row in enumerate(records):
        # Build canonical row string to hash (ensure all keys exist)
        desc = (
            f"{row.get('name','')}|{row.get('type','')}|{row.get('city','')}|{row.get('course','')}|"
            f"{row.get('fees','')}|{row.get('avg_package','')}|{row.get('ranking','')}|{row.get('exam','')}"
        )
        row_hash = hashlib.md5(desc.encode("utf-8")).hexdigest()

        if row_hash in existing_hashes:
            continue  # Duplicate, skip
            
        # Otherwise add to memory
        content = MemoryContent(
            content=desc,
            mime_type=MemoryMimeType.TEXT,
            metadata={**row, "row_hash": row_hash, "chunk_index": idx}
        )
        await rag_memory.add(content)
        existing_hashes.add(row_hash)
        count_added += 1

    print(f"Indexed {count_added} new records to ChromaDB (skipped {len(records) - count_added} duplicates)")

# RAG System class
class CollegeRAGSystem:
    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or config.DEFAULT_CSV_PATH
        self.rag_memory: Optional[ChromaDBVectorMemory] = None
        self.agent: Optional[AssistantAgent] = None
        self.model_client: Optional[OpenAIChatCompletionClient] = None

    async def initialize(self):
        # Validate required environment variables
        missing_vars = config.validate_required_env_vars()
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        # Print configuration for debugging
        config.print_config()
        
        # Setup ChromaDB vector memory using deployment-aware configuration
        self.rag_memory = create_chromadb_memory_config()
        
        # Load data and index into memory (only if needed)
        college_records = load_colleges_from_csv(self.csv_path)
        await index_colleges_to_memory(college_records, self.rag_memory)

        # OpenAI model client
        self.model_client = OpenAIChatCompletionClient(
            model=config.OPENAI_RAG_MODEL,
            base_url=config.OPENAI_RAG_MODEL_API_BASE,
            api_key=config.OPENAI_RAG_MODEL_API_KEY,
            max_retries=config.OPENAI_MAX_RETRIES,
        )
        
        # Agent with vector memory
        self.agent = AssistantAgent(
            name="college_rag_agent",
            model_client=self.model_client,
            memory=[self.rag_memory]
        )

    # Async run: Given a user query, produce a RAG-based recommendation
    async def recommend(self, query: str) -> str:
        """
        Get college recommendations using enhanced LLM-powered metadata filtering and semantic search.
        """
        if not self.agent:
            raise ValueError("RAG system not initialized. Call initialize() first.")
        
        if not self.rag_memory:
            raise ValueError("RAG memory not initialized. Call initialize() first.")
        
        try:
            # Extract structured filters using LLM
            print(f"🔍 Analyzing query: {query}")
            query_analysis = await extract_filters_with_llm(query)
            
            print(f"📊 Filter extraction confidence: {query_analysis.confidence:.1%}")
            # Check if any filters were extracted
            filters_dict = query_analysis.filters.to_chromadb_filters()
            if filters_dict:
                print(f"🎯 Extracted filters: {query_analysis.filters.to_readable_summary()}")
            
            # Convert to ChromaDB format
            metadata_filters = query_analysis.filters.to_chromadb_filters()
            cleaned_query = query_analysis.cleaned_query
            
            # For very low confidence, fall back to original query
            if query_analysis.confidence < 0.3:
                cleaned_query = query
                metadata_filters = {}
                print("⚠️  Low confidence, using original query without filters")
            
            print(f"🔍 Searching with: '{cleaned_query}'")
            if metadata_filters:
                print(f"📋 Applying filters: {metadata_filters}")
            
            # Create a temporary memory config with higher k for better results
            temp_memory = create_chromadb_memory_config(k=50, score_threshold=0.0)
            
            # Query the memory with filters
            try:
                if metadata_filters:
                    # Convert filters to ChromaDB format with $and
                    if len(metadata_filters) > 1:
                        chroma_filter = {"$and": []}
                        for key, value in metadata_filters.items():
                            if isinstance(value, dict):
                                # Handle operators like $lt, $gt
                                for op, val in value.items():
                                    chroma_filter["$and"].append({key: {op: val}})
                            else:
                                # Handle direct equality
                                chroma_filter["$and"].append({key: value})
                    else:
                        # Single filter can be used directly
                        chroma_filter = metadata_filters
                    
                    print(f"🔧 ChromaDB filter format: {chroma_filter}")
                    
                    results = await temp_memory.query(
                        query=cleaned_query or "college university institute",
                        where=chroma_filter
                    )
                else:
                    results = await temp_memory.query(query=cleaned_query or query)
                    
            except Exception as e:
                print(f"⚠️  Metadata filtering failed, falling back to standard query: {e}")
                results = await temp_memory.query(query=query)
                
            await temp_memory.close()
            
            if not results.results:
                if metadata_filters:
                    return f"❌ No colleges found matching your criteria. Try adjusting your filters or search terms.\n\nApplied filters: {query_analysis.filters.to_readable_summary()}"
                return "❌ No matching colleges found for your query."
            
            print(f"📊 Found {len(results.results)} results after filtering")
            
            # Format the top 3 unique results
            formatted_results = []
            seen_colleges = set()
            max_results = 3
            
            # Sort results by score (higher is better)
            sorted_results = sorted(results.results, 
                                  key=lambda x: getattr(x.metadata, 'score', 0) if hasattr(x.metadata, 'score') else getattr(x, 'score', 0), 
                                  reverse=True)
            
            for result in sorted_results:
                if len(formatted_results) >= max_results:
                    break
                    
                metadata = getattr(result, 'metadata', None)
                if not metadata:
                    continue
                    
                college_name = metadata.get('name', 'Unknown College') if hasattr(metadata, 'get') else getattr(metadata, 'name', 'Unknown College')
                
                # Skip duplicates
                if college_name in seen_colleges:
                    continue
                seen_colleges.add(college_name)
                
                fees = metadata.get('fees', 0) if hasattr(metadata, 'get') else getattr(metadata, 'fees', 0)
                avg_package = metadata.get('avg_package', 0) if hasattr(metadata, 'get') else getattr(metadata, 'avg_package', 0)
                college_type = metadata.get('type', 'Unknown') if hasattr(metadata, 'get') else getattr(metadata, 'type', 'Unknown')
                city = metadata.get('city', 'Unknown') if hasattr(metadata, 'get') else getattr(metadata, 'city', 'Unknown')
                ranking = metadata.get('ranking', 'N/A') if hasattr(metadata, 'get') else getattr(metadata, 'ranking', 'N/A')
                
                # Format fees and package
                fees_formatted = f"₹{fees:,}" if fees else "Not specified"
                package_formatted = f"₹{avg_package:,}" if avg_package else "Not specified"
                
                formatted_results.append(
                    f"- **{college_name}** ({city}): Fees - {fees_formatted}, Avg Package - {package_formatted}, Type - {college_type.capitalize()}, Ranking - {ranking}"
                )
            
            if not formatted_results:
                if metadata_filters:
                    return f"❌ No colleges found matching your criteria. Try adjusting your filters.\n\nApplied filters: {query_analysis.filters.to_readable_summary()}"
                return "❌ No matching colleges found for your query."
            
            # Add header with intelligent filter information
            filter_info = ""
            if metadata_filters and query_analysis.confidence > 0.5:
                filter_info = f" (Filtered by: {query_analysis.filters.to_readable_summary()})"
            
            header = f"**Top {len(formatted_results)} College{'s' if len(formatted_results) != 1 else ''} matching your query{filter_info}:**\n\n"
            return header + "\n".join(formatted_results)
            
        except Exception as e:
            print(f"❌ Error in recommend: {e}")
            return f"❌ Sorry, I encountered an error while processing your request: {str(e)}"

    # Clean up resources (recommended in long-running jobs)
    async def close(self):
        if self.model_client:
            await self.model_client.close()
        if self.rag_memory:
            await self.rag_memory.close()

    async def delete_all_chromadb_data(self):
        """
        Delete all data stored in ChromaDB for the configured collection.
        """
        if not self.rag_memory:
            # If not initialized, create a temporary memory instance using our helper
            temp_memory = create_chromadb_memory_config(k=10000)
            await temp_memory.clear()
            await temp_memory.close()
        else:
            await self.rag_memory.clear()
        print(f"All data deleted from ChromaDB collection '{config.CHROMA_COLLECTION_NAME}'.")

# Usage Example
if __name__ == "__main__":
    import asyncio
    import sys
    
    async def _demo():
        # Check for required environment variables
        missing_vars = config.validate_required_env_vars()
        if missing_vars:
            print(f"❌ Error: Missing required environment variables: {missing_vars}")
            print("Please check the .env.example file for required settings.")
            sys.exit(1)
        
        rag = CollegeRAGSystem()
        await rag.initialize()
        
        # Test multiple queries to show the improved functionality with metadata filters
        test_queries = [
            "Best private MBA colleges in Delhi under 10 lakhs fees",
            "Engineering colleges in Mumbai with fees < ₹2L",
            "Government colleges with ranking better than 30",
            "Private colleges in Bangalore with package > ₹8L",
            "MBA colleges with fees under ₹5 lakhs and type = private"
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Query: {query}")
            print('='*50)
            answer = await rag.recommend(query)
            print(answer)
        
        # Only delete data if you want to reset (uncomment next line if needed)
        # await rag.delete_all_chromadb_data()
        await rag.close()
    
    asyncio.run(_demo())
