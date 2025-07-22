#!/usr/bin/env python3
"""
FastAPI application for Smart Campus Guide - College Recommendation System
Provides REST API endpoints for college recommendations using RAG system.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.rag.simplified_rag import SimplifiedCollegeRAGSystem
from src.constants import config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG system instance
rag_system: Optional[SimplifiedCollegeRAGSystem] = None


class RecommendationRequest(BaseModel):
    """Request model for college recommendations."""
    query: str = Field(..., description="Natural language query for college search", min_length=1, max_length=500)
    include_analysis: bool = Field(False, description="Include query analysis details in response")


class RecommendationResponse(BaseModel):
    """Response model for college recommendations."""
    query: str = Field(..., description="Original query")
    recommendations: str = Field(..., description="Formatted college recommendations")
    success: bool = Field(..., description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Additional message or error details")
    analysis: Optional[Dict[str, Any]] = Field(None, description="Query analysis details if requested")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    rag_system_initialized: bool = Field(..., description="Whether RAG system is ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - initialize and cleanup RAG system."""
    global rag_system
    
    logger.info("🚀 Starting Smart Campus Guide API...")
    
    try:
        # Validate environment variables
        missing_vars = config.validate_required_env_vars()
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        # Initialize RAG system
        logger.info("🔧 Initializing RAG system...")
        rag_system = SimplifiedCollegeRAGSystem()
        await rag_system.initialize()
        logger.info("✅ RAG system initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG system: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up RAG system...")
        if rag_system:
            await rag_system.close()
        logger.info("👋 Smart Campus Guide API shutdown complete")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="Smart Campus Guide API",
    description="AI-powered college recommendation system using RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to Smart Campus Guide API",
        "description": "AI-powered college recommendation system",
        "version": "1.0.0",
        "endpoints": "Visit /docs for interactive API documentation"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        rag_system_initialized=rag_system is not None
    )


@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get college recommendations based on natural language query.
    
    This endpoint uses an AI-powered RAG system to understand user queries
    and provide personalized college recommendations with intelligent filtering.
    
    Example queries:
    - "MBA colleges in Delhi under 10 lakhs"
    - "Best engineering colleges in Mumbai"
    - "Private medical colleges with good placement"
    - "Law colleges with fees under 5 lakhs"
    """
    if not rag_system:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Please try again later."
        )
    
    try:
        logger.info(f"📝 Processing recommendation request: {request.query}")
        
        # Get recommendations from RAG system
        recommendations = await rag_system.recommend(request.query)
        
        # Prepare response
        response = RecommendationResponse(
            query=request.query,
            recommendations=recommendations,
            success=True,
            message=None,
            analysis=None
        )
        
        # Add analysis details if requested
        if request.include_analysis:
            # You could extract more detailed analysis here if needed
            response.analysis = {
                "processed": True,
                "query_length": len(request.query),
                "timestamp": "2024-01-01T00:00:00Z"  # You could add actual timestamp
            }
        
        logger.info(f"✅ Successfully processed recommendation for: {request.query}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing recommendation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/recommend/batch")
async def get_batch_recommendations(queries: list[str], background_tasks: BackgroundTasks):
    """
    Get recommendations for multiple queries (batch processing).
    Useful for processing multiple queries efficiently.
    """
    if not rag_system:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Please try again later."
        )
    
    if len(queries) > 10:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Batch size limited to 10 queries"
        )
    
    try:
        results = []
        for query in queries:
            if not query.strip():
                continue
                
            logger.info(f"📝 Processing batch query: {query}")
            recommendations = await rag_system.recommend(query)
            results.append({
                "query": query,
                "recommendations": recommendations,
                "success": True
            })
        
        return {
            "results": results,
            "total_processed": len(results),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error in batch processing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing error: {str(e)}"
        )


@app.get("/config")
async def get_config():
    """Get current system configuration (non-sensitive information only)."""
    return {
        "rag_k": config.RAG_K,
        "score_threshold": config.RAG_SCORE_THRESHOLD,
        "collection_name": config.CHROMA_COLLECTION_NAME,
        "embedding_model": config.EMBEDDING_MODEL_NAME,
        "openai_model": config.OPENAI_RAG_MODEL,
        "chunk_size": config.RAG_CHUNK_SIZE
    }


def main():
    """Main function to run the FastAPI application."""
    logger.info("🚀 Starting Smart Campus Guide API server...")
    
    # Check environment variables before starting
    missing_vars = config.validate_required_env_vars()
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("Please check the .env.example file for required settings.")
        return
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Changed to avoid conflict with kubectl
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    main()
