import hashlib
import os
import pandas as pd
import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Dict, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.memory.chromadb import (
    ChromaDBVectorMemory,
    PersistentChromaDBVectorMemoryConfig,
    SentenceTransformerEmbeddingFunctionConfig,
)
from autogen_core.memory import MemoryContent, MemoryMimeType

from constants import config

# Helper: Load college records and chunk
def load_colleges_from_csv(csv_path: str) -> List[Dict]:
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient='records')
    return records

# Async: Index all colleges into ChromaDB vector memory
async def index_colleges_to_memory(records, rag_memory: ChromaDBVectorMemory, chunk_size: Optional[int] = None):
    """
    Index colleges, avoiding duplicate entries by hash.
    """
    chunk_size = chunk_size or config.RAG_CHUNK_SIZE

    # Build a set of existing hashes from current memory
    existing_hashes = set()
    rag_memory = ChromaDBVectorMemory(
            config=PersistentChromaDBVectorMemoryConfig(
                collection_name=config.CHROMA_COLLECTION_NAME,
                persistence_path=config.CHROMA_PERSIST_DIRECTORY,
                k=10000,  # high k for full scan
                score_threshold=config.RAG_SCORE_THRESHOLD,
                embedding_function_config=SentenceTransformerEmbeddingFunctionConfig(
                    model_name=config.EMBEDDING_MODEL_NAME
                ),
            )
        )

    # Query all current memory items (could limit by collection size for large sets)
    results = await rag_memory.query(
        query="",  # Blank query for full scan
    )
    if not results.results:
        print("No existing records found in ChromaDB, starting fresh indexing.")
    else:
        print(f"Found {len(results.results)} existing records in ChromaDB, checking for duplicates.")
        for result in results.results:
            meta = getattr(result, "metadata", None)
            if meta and "row_hash" in meta:
                existing_hashes.add(meta["row_hash"])

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
        
        # Setup persistent ChromaDB vector memory
        self.rag_memory = ChromaDBVectorMemory(
            config=PersistentChromaDBVectorMemoryConfig(
                collection_name=config.CHROMA_COLLECTION_NAME,
                persistence_path=config.CHROMA_PERSIST_DIRECTORY,
                k=config.RAG_K,
                score_threshold=config.RAG_SCORE_THRESHOLD,
                embedding_function_config=SentenceTransformerEmbeddingFunctionConfig(
                    model_name=config.EMBEDDING_MODEL_NAME
                ),
            )
        )
        
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
        if not self.agent:
            raise ValueError("RAG system not initialized. Call initialize() first.")
        
        if not self.rag_memory:
            raise ValueError("RAG memory not initialized. Call initialize() first.")
        
        # Create a temporary memory config with higher k and lower score threshold for better results
        temp_memory = ChromaDBVectorMemory(
            config=PersistentChromaDBVectorMemoryConfig(
                collection_name=config.CHROMA_COLLECTION_NAME,
                persistence_path=config.CHROMA_PERSIST_DIRECTORY,
                k=25,  # Get all results first
                score_threshold=0.0,  # No score filtering, we'll rank by relevance
                embedding_function_config=SentenceTransformerEmbeddingFunctionConfig(
                    model_name=config.EMBEDDING_MODEL_NAME
                ),
            )
        )
        
        # Query the memory directly to get relevant colleges
        results = await temp_memory.query(query=query)
        await temp_memory.close()  # Clean up the temporary memory
        
        if not results.results:
            return "No matching colleges found for your query."
        
        # Format the top 3 unique results as a clean markdown list
        formatted_results = []
        seen_colleges = set()  # To avoid duplicates
        max_results = 3
        
        # Sort results by score (higher is better for similarity)
        sorted_results = sorted(results.results, 
                              key=lambda x: getattr(x.metadata, 'score', 0) if hasattr(x.metadata, 'score') else getattr(x, 'score', 0), 
                              reverse=True)
        
        # Iterate through all results to find top 3 unique colleges
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
            
            # Format fees and package in a readable way
            fees_formatted = f"₹{fees:,}" if fees else "Not specified"
            package_formatted = f"₹{avg_package:,}" if avg_package else "Not specified"
            
            # Enhanced formatting with more details
            formatted_results.append(
                f"- **{college_name}** ({city}): Fees - {fees_formatted}, Avg Package - {package_formatted}, Type - {college_type.capitalize()}, Ranking - {ranking}"
            )
        
        if not formatted_results:
            return "No matching colleges found for your query."
        
        # Add a header and return the formatted list
        header = f"**Top {len(formatted_results)} College{'s' if len(formatted_results) != 1 else ''} matching your query:**\n\n"
        return header + "\n".join(formatted_results)

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
            # If not initialized, create a temporary memory instance
            temp_memory = ChromaDBVectorMemory(
                config=PersistentChromaDBVectorMemoryConfig(
                    collection_name=config.CHROMA_COLLECTION_NAME,
                    persistence_path=config.CHROMA_PERSIST_DIRECTORY,
                    k=10000,
                    score_threshold=config.RAG_SCORE_THRESHOLD,
                    embedding_function_config=SentenceTransformerEmbeddingFunctionConfig(
                        model_name=config.EMBEDDING_MODEL_NAME
                    ),
                )
            )
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
        
        # Test multiple queries to show the improved functionality
        test_queries = [
            "Best private MBA colleges in Delhi under 10 lakhs fees",
            "Top engineering colleges in Mumbai",
            "Government colleges for MBA in India"
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
