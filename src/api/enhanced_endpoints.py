#!/usr/bin/env python3
"""
Enhanced FastAPI endpoints for better Streamlit integration.
Additional endpoints for frontend functionality.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from src.constants import config

# Create router for enhanced endpoints
enhanced_router = APIRouter(prefix="/api/v1", tags=["Enhanced"])

logger = logging.getLogger(__name__)


class QuerySuggestion(BaseModel):
    """Model for query suggestions."""
    suggestion: str = Field(..., description="Suggested query text")
    category: str = Field(..., description="Query category")
    description: str = Field(..., description="Description of what this query finds")


class SearchStats(BaseModel):
    """Model for search statistics."""
    total_queries: int = Field(..., description="Total number of queries processed")
    popular_categories: List[str] = Field(..., description="Most popular search categories")
    average_response_time: float = Field(..., description="Average response time in seconds")
    success_rate: float = Field(..., description="Query success rate percentage")


class SystemMetrics(BaseModel):
    """Model for system metrics."""
    uptime: str = Field(..., description="System uptime")
    memory_usage: float = Field(..., description="Memory usage percentage")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    active_connections: int = Field(..., description="Number of active connections")


@enhanced_router.get("/suggestions", response_model=List[QuerySuggestion])
async def get_query_suggestions(
    category: Optional[str] = Query(None, description="Filter suggestions by category")
):
    """
    Get query suggestions for users.
    Helps users understand what kinds of queries work well.
    """
    suggestions = [
        # Course-based suggestions
        QuerySuggestion(
            suggestion="MBA colleges in Mumbai with good placements",
            category="course",
            description="Find MBA programs in Mumbai with strong placement records"
        ),
        QuerySuggestion(
            suggestion="Engineering colleges in Bangalore under 5 lakhs",
            category="course",
            description="Affordable engineering colleges in Bangalore"
        ),
        QuerySuggestion(
            suggestion="Medical colleges in Delhi with NEET acceptance",
            category="course",
            description="Medical colleges in Delhi that accept NEET scores"
        ),
        QuerySuggestion(
            suggestion="Law colleges in Chennai with moot court facilities",
            category="course",
            description="Law colleges in Chennai with practical legal training"
        ),
        
        # Budget-based suggestions
        QuerySuggestion(
            suggestion="Private colleges under 3 lakhs fees",
            category="budget",
            description="Affordable private colleges across India"
        ),
        QuerySuggestion(
            suggestion="Engineering colleges with fees between 2-5 lakhs",
            category="budget",
            description="Mid-range engineering colleges by fee structure"
        ),
        QuerySuggestion(
            suggestion="MBA programs under 10 lakhs in tier-1 cities",
            category="budget",
            description="Affordable MBA programs in major cities"
        ),
        
        # Ranking-based suggestions
        QuerySuggestion(
            suggestion="Top 20 engineering colleges in India",
            category="ranking",
            description="Highest ranked engineering institutions"
        ),
        QuerySuggestion(
            suggestion="Highly ranked business schools in Bangalore",
            category="ranking",
            description="Premier business schools in Bangalore"
        ),
        QuerySuggestion(
            suggestion="Government colleges with good rankings",
            category="ranking",
            description="Top-ranked government institutions"
        ),
        
        # Location-based suggestions
        QuerySuggestion(
            suggestion="Colleges in NCR region for computer science",
            category="location",
            description="CS programs in National Capital Region"
        ),
        QuerySuggestion(
            suggestion="Best colleges in South India for biotechnology",
            category="location",
            description="Biotechnology programs in southern states"
        ),
        QuerySuggestion(
            suggestion="Engineering colleges in tier-2 cities",
            category="location",
            description="Quality engineering education in smaller cities"
        )
    ]
    
    # Filter by category if specified
    if category:
        suggestions = [s for s in suggestions if s.category.lower() == category.lower()]
    
    return suggestions


@enhanced_router.get("/categories")
async def get_search_categories():
    """
    Get available search categories.
    Helps organize suggestions and queries.
    """
    categories = [
        {
            "name": "course",
            "display_name": "Course-based",
            "description": "Search by specific courses or programs",
            "icon": "🎓",
            "examples": ["MBA", "Engineering", "Medical", "Law"]
        },
        {
            "name": "budget",
            "display_name": "Budget-based",
            "description": "Search by fee range and affordability",
            "icon": "💰",
            "examples": ["Under 5 lakhs", "Between 2-8 lakhs", "Premium colleges"]
        },
        {
            "name": "ranking",
            "display_name": "Ranking-based",
            "description": "Search by rankings and reputation",
            "icon": "🏆",
            "examples": ["Top 10", "Highly ranked", "Premier institutions"]
        },
        {
            "name": "location",
            "display_name": "Location-based",
            "description": "Search by city, state, or region",
            "icon": "📍",
            "examples": ["Mumbai", "South India", "Tier-1 cities"]
        },
        {
            "name": "facilities",
            "display_name": "Facilities-based",
            "description": "Search by specific facilities or amenities",
            "icon": "🏢",
            "examples": ["Hostel", "Research labs", "Sports facilities"]
        },
        {
            "name": "placement",
            "display_name": "Placement-based",
            "description": "Search by placement records and packages",
            "icon": "💼",
            "examples": ["Good placements", "High packages", "Top recruiters"]
        }
    ]
    
    return {"categories": categories}


@enhanced_router.get("/stats", response_model=SearchStats)
async def get_search_stats():
    """
    Get search statistics and analytics.
    Provides insights into system usage.
    """
    # In a real implementation, these would come from a database
    # For now, return mock data
    return SearchStats(
        total_queries=1247,
        popular_categories=["course", "budget", "location", "ranking"],
        average_response_time=2.3,
        success_rate=94.2
    )


@enhanced_router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """
    Get system performance metrics.
    Useful for monitoring and debugging.
    """
    import psutil
    import time
    from datetime import timedelta
    
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get uptime (simplified)
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime = str(timedelta(seconds=int(uptime_seconds)))
        
        return SystemMetrics(
            uptime=uptime,
            memory_usage=memory.percent,
            cpu_usage=cpu_percent,
            active_connections=len(psutil.net_connections())
        )
    
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        # Return default values if psutil fails
        return SystemMetrics(
            uptime="Unknown",
            memory_usage=0.0,
            cpu_usage=0.0,
            active_connections=0
        )


@enhanced_router.get("/validate-query")
async def validate_query(query: str = Query(..., description="Query to validate")):
    """
    Validate a query before processing.
    Helps provide feedback to users.
    """
    if not query or len(query.strip()) < 3:
        return {
            "valid": False,
            "reason": "Query too short",
            "suggestion": "Please provide a more detailed query with at least 3 characters"
        }
    
    if len(query) > 500:
        return {
            "valid": False,
            "reason": "Query too long",
            "suggestion": "Please keep your query under 500 characters"
        }
    
    # Check for common keywords that indicate a good query
    good_keywords = [
        "college", "university", "mba", "engineering", "medical", "law",
        "fees", "under", "above", "ranking", "placement", "government",
        "private", "delhi", "mumbai", "bangalore", "chennai", "pune",
        "hyderabad", "kolkata", "ahmedabad", "lakhs", "crore"
    ]
    
    query_lower = query.lower()
    has_good_keywords = any(keyword in query_lower for keyword in good_keywords)
    
    if not has_good_keywords:
        return {
            "valid": True,
            "reason": "Generic query",
            "suggestion": "Consider adding specific details like location, course, or budget for better results"
        }
    
    return {
        "valid": True,
        "reason": "Good query",
        "suggestion": "Your query looks good and should return relevant results"
    }


@enhanced_router.get("/popular-queries")
async def get_popular_queries(limit: int = Query(10, description="Number of queries to return")):
    """
    Get popular/trending queries.
    Helps users discover common search patterns.
    """
    # In a real implementation, this would come from analytics data
    popular_queries = [
        {
            "query": "MBA colleges in Mumbai under 10 lakhs",
            "count": 156,
            "category": "course",
            "trend": "up"
        },
        {
            "query": "Engineering colleges in Bangalore with good placements",
            "count": 142,
            "category": "course", 
            "trend": "stable"
        },
        {
            "query": "Medical colleges in Delhi",
            "count": 134,
            "category": "course",
            "trend": "up"
        },
        {
            "query": "Private colleges under 5 lakhs",
            "count": 128,
            "category": "budget",
            "trend": "down"
        },
        {
            "query": "Top engineering colleges in India",
            "count": 121,
            "category": "ranking",
            "trend": "stable"
        },
        {
            "query": "Law colleges in Chennai",
            "count": 95,
            "category": "course",
            "trend": "up"
        },
        {
            "query": "Computer science colleges in Pune",
            "count": 89,
            "category": "course",
            "trend": "stable"
        },
        {
            "query": "Government engineering colleges",
            "count": 87,
            "category": "ranking",
            "trend": "up"
        },
        {
            "query": "MBA colleges with scholarships",
            "count": 82,
            "category": "course",
            "trend": "up"
        },
        {
            "query": "Colleges in tier 2 cities",
            "count": 76,
            "category": "location",
            "trend": "stable"
        }
    ]
    
    return {"queries": popular_queries[:limit]}


@enhanced_router.get("/export-results")
async def export_search_results(
    query: str = Query(..., description="Original search query"),
    format: str = Query("json", description="Export format: json, csv, or txt")
):
    """
    Export search results in different formats.
    Useful for saving and sharing results.
    """
    # This would integrate with the main recommendation system
    # For now, return a mock response
    
    if format not in ["json", "csv", "txt"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use json, csv, or txt")
    
    # Mock result data
    results = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "results": [
            {
                "college_name": "Example College 1",
                "location": "Mumbai",
                "fees": "₹8,00,000",
                "course": "MBA",
                "ranking": "Top 50"
            },
            {
                "college_name": "Example College 2", 
                "location": "Delhi",
                "fees": "₹6,50,000",
                "course": "MBA",
                "ranking": "Top 75"
            }
        ]
    }
    
    if format == "json":
        return results
    elif format == "csv":
        # Convert to CSV format
        csv_data = "College Name,Location,Fees,Course,Ranking\n"
        for result in results["results"]:
            csv_data += f"{result['college_name']},{result['location']},{result['fees']},{result['course']},{result['ranking']}\n"
        return {"format": "csv", "data": csv_data}
    else:  # txt format
        txt_data = f"Search Results for: {query}\n"
        txt_data += f"Generated: {results['timestamp']}\n\n"
        for i, result in enumerate(results["results"], 1):
            txt_data += f"{i}. {result['college_name']}\n"
            txt_data += f"   Location: {result['location']}\n"
            txt_data += f"   Fees: {result['fees']}\n"
            txt_data += f"   Course: {result['course']}\n"
            txt_data += f"   Ranking: {result['ranking']}\n\n"
        return {"format": "txt", "data": txt_data}


# Add the enhanced router to the main FastAPI app
# This would be imported in main.py: app.include_router(enhanced_router)
