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
            
        # Compose a recommendation prompt
        rag_task = (
            f"Based on the following query, recommend the top 3 matching Indian colleges from the memory store. "
            f"Present the match as a markdown bullet list (college, fees, avg package, type). Query: {query}"
        )
        # Run agent and collect streaming output
        stream = self.agent.run_stream(task=rag_task)
        # AsyncGenerator[BaseAgentEvent | BaseChatMessage | TaskResult, None]
        response = ""
        async for chunk in stream:
            if hasattr(chunk, "content"):
                response += str(getattr(chunk, "content"))
        return response.strip()

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
        query = "Best private MBA colleges in Delhi under 10 lakhs fees"
        print("Query:", query)
        answer = await rag.recommend(query)
        print("\nResult:\n", answer)
        await rag.delete_all_chromadb_data()
        await rag.close()
    
    asyncio.run(_demo())
