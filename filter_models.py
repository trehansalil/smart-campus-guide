"""
Pydantic models for structured metadata filtering in the Smart Campus Guide RAG system.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class CollegeType(str, Enum):
    """Enum for college types"""
    PRIVATE = "private"
    GOVERNMENT = "govt"
    PUBLIC = "govt"  # Alias for government

class ComparisonOperator(str, Enum):
    """Enum for comparison operators"""
    LESS_THAN = "lt"
    LESS_THAN_EQUAL = "lte" 
    GREATER_THAN = "gt"
    GREATER_THAN_EQUAL = "gte"
    EQUAL = "eq"

class NumericFilter(BaseModel):
    """Model for numeric filters with comparison operators"""
    value: float
    operator: ComparisonOperator
    
    def to_chromadb_filter(self) -> dict:
        """Convert to ChromaDB filter format"""
        op_map = {
            "lt": "$lt",
            "lte": "$lte", 
            "gt": "$gt",
            "gte": "$gte",
            "eq": "$eq"
        }
        return {op_map[self.operator]: self.value}

class CollegeFilters(BaseModel):
    """
    Structured model for college search filters extracted from natural language queries.
    """
    
    # College metadata filters
    city: Optional[str] = Field(None, description="City where the college is located")
    state: Optional[str] = Field(None, description="State where the college is located")
    course: Optional[str] = Field(None, description="Course/program offered (MBA, Engineering, etc.)")
    college_type: Optional[str] = Field(None, description="Type of college (private, govt, deemed)")
    
    # Numeric filters with operators
    fees: Optional[NumericFilter] = Field(None, description="Annual fees filter")
    avg_package: Optional[NumericFilter] = Field(None, description="Average package filter")
    ranking: Optional[NumericFilter] = Field(None, description="Ranking filter")
    
    # Additional filters
    exam: Optional[str] = Field(None, description="Entrance exam required (CAT, JEE, etc.)")
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
    
    @validator('city', 'state', pre=True)
    def title_case_location(cls, v):
        """Convert location names to title case"""
        return v.title() if v else v
        
    @validator('exam', pre=True)
    def uppercase_exam(cls, v):
        """Convert exam names to uppercase"""
        return v.upper() if v else v

    def to_chromadb_filters(self) -> dict:
        """
        Convert the Pydantic model to ChromaDB filter format.
        
        Returns:
            dict: ChromaDB-compatible filter dictionary
        """
        filters = {}
        
        # Simple equality filters
        if self.city:
            filters['city'] = self.city
        if self.state:
            filters['state'] = self.state
        if self.course:
            filters['course'] = self.course
        if self.college_type:
            # Store directly as string to match ChromaDB data
            filters['type'] = self.college_type.lower()
        if self.exam:
            filters['exam'] = self.exam
            
        # Numeric filters with operators
        if self.fees:
            filters['fees'] = self.fees.to_chromadb_filter()
        if self.avg_package:
            filters['avg_package'] = self.avg_package.to_chromadb_filter()
        if self.ranking:
            filters['ranking'] = self.ranking.to_chromadb_filter()
            
        return filters
    
    def to_readable_summary(self) -> str:
        """
        Convert filters to a human-readable summary.
        
        Returns:
            str: Human-readable description of applied filters
        """
        parts = []
        
        if self.city:
            parts.append(f"in {self.city}")
        if self.state:
            parts.append(f"in {self.state} state")
        if self.course:
            parts.append(f"for {self.course}")
        if self.college_type:
            parts.append(f"{self.college_type.lower()} colleges")
            
        if self.fees:
            op_text = {
                "lt": "under", "lte": "up to", "gt": "above", 
                "gte": "at least", "eq": "exactly"
            }[self.fees.operator]
            amount = f"₹{self.fees.value:,.0f}"
            if self.fees.value >= 100000:
                amount = f"₹{self.fees.value/100000:.1f}L"
            parts.append(f"fees {op_text} {amount}")
            
        if self.avg_package:
            op_text = {
                "lt": "under", "lte": "up to", "gt": "above",
                "gte": "at least", "eq": "exactly"  
            }[self.avg_package.operator]
            amount = f"₹{self.avg_package.value:,.0f}"
            if self.avg_package.value >= 100000:
                amount = f"₹{self.avg_package.value/100000:.1f}L"
            parts.append(f"package {op_text} {amount}")
            
        if self.ranking:
            op_text = {
                "lt": "better than rank", "lte": "rank up to", "gt": "rank worse than",
                "gte": "rank at least", "eq": "rank exactly"
            }[self.ranking.operator]
            parts.append(f"{op_text} {self.ranking.value:.0f}")
            
        if self.exam:
            parts.append(f"accepting {self.exam}")
            
        return ", ".join(parts) if parts else "no specific filters"

class QueryAnalysis(BaseModel):
    """
    Complete analysis of a user query including extracted filters and cleaned query.
    """
    original_query: str = Field(..., description="The original user query")
    filters: CollegeFilters = Field(..., description="Extracted structured filters")
    cleaned_query: str = Field(..., description="Query with filter terms removed")
    intent: str = Field(..., description="Primary intent of the query (search, compare, recommend, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the extraction (0-1)")
    
    def get_search_terms(self) -> str:
        """Get the cleaned query terms for semantic search"""
        if self.cleaned_query.strip():
            return self.cleaned_query
        elif self.filters.course:
            return f"{self.filters.course} colleges"
        else:
            return "colleges universities institutes"
