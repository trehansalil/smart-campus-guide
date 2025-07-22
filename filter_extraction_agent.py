"""
LLM-powered filter extraction agent for the Smart Campus Guide RAG system.
"""

import json
import asyncio
from typing import Optional
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from filter_models import CollegeFilters, QueryAnalysis, NumericFilter, ComparisonOperator, CollegeType
from constants import config

class FilterExtractionAgent:
    """
    LLM-powered agent that extracts structured filters from natural language queries.
    """
    
    def __init__(self):
        self.model_client: Optional[OpenAIChatCompletionClient] = None
        self.agent: Optional[AssistantAgent] = None
    
    async def initialize(self):
        """Initialize the LLM client and agent"""
        # Use the same OpenAI configuration as the main RAG system
        self.model_client = OpenAIChatCompletionClient(
            model=config.OPENAI_RAG_MODEL,
            base_url=config.OPENAI_RAG_MODEL_API_BASE,
            api_key=config.OPENAI_RAG_MODEL_API_KEY,
            max_retries=config.OPENAI_MAX_RETRIES,
        )
        
        # Create agent with specialized system prompt for filter extraction
        system_prompt = self._get_system_prompt()
        
        self.agent = AssistantAgent(
            name="filter_extraction_agent",
            model_client=self.model_client,
            system_message=system_prompt
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for filter extraction"""
        return """You are an expert at extracting structured college search filters from natural language queries.

Your task is to analyze user queries about colleges and extract specific filter criteria into a structured JSON format.

**Supported Filters:**
- city: String (e.g., "Mumbai", "Delhi", "Bangalore")
- state: String (e.g., "Maharashtra", "Karnataka") 
- fees: Numeric with operator (lt/lte/gt/gte/eq) and value in actual rupees
- avg_package: Numeric with operator and value in actual rupees
- ranking: Numeric with operator and value (lower numbers = better ranking)
- course: String (e.g., "MBA", "ENGINEERING", "MEDICAL")
- college_type: Enum ("Private", "Govt")
- exam: String (e.g., "CAT", "JEE", "NEET")

**Important Rules:**
1. Convert lakhs to actual amounts (5 lakhs = 500000)
2. For ranking: "better than 30" means ranking < 30 (operator: "lt")
3. For fees: "under 10 lakhs" means fees < 1000000 (operator: "lt")
4. Normalize college types: government/govt/public → "Govt", private → "Private"
5. Extract city names from phrases like "in Mumbai", "Delhi colleges"
6. Remove filter terms from cleaned_query but keep intent words

**Output Format:**
Always respond with valid JSON containing:
- filters: Object with extracted filters
- cleaned_query: String with filter terms removed
- intent: String describing the primary intent
- confidence: Float between 0.0-1.0

**Examples:**

Query: "Best MBA colleges in Delhi under 10 lakhs fees"
```json
{
  "filters": {
    "city": "Delhi",
    "course": "MBA", 
    "fees": {"value": 1000000, "operator": "lt"}
  },
  "cleaned_query": "best colleges",
  "intent": "find_colleges",
  "confidence": 0.9
}
```

Query: "Private engineering colleges in Mumbai with ranking better than 25"
```json
{
  "filters": {
    "city": "Mumbai",
    "course": "ENGINEERING",
    "college_type": "Private",
    "ranking": {"value": 25, "operator": "lt"}
  },
  "cleaned_query": "colleges",
  "intent": "find_colleges", 
  "confidence": 0.95
}
```

Query: "Government colleges with package above 8 lakhs"
```json
{
  "filters": {
    "college_type": "Govt",
    "avg_package": {"value": 800000, "operator": "gt"}
  },
  "cleaned_query": "colleges",
  "intent": "find_colleges",
  "confidence": 0.85
}
```

Analyze the following query and extract filters in the exact JSON format shown above:"""

    async def extract_filters_simple(self, query: str) -> QueryAnalysis:
        """
        Simple extraction using OpenAI client directly for now.
        TODO: Replace with proper autogen agent once API is clarified.
        """
        try:
            # Use the model client directly
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": query}
            ]
            
            # Make direct API call for now
            import openai
            client = openai.AsyncOpenAI(
                api_key=config.OPENAI_RAG_MODEL_API_KEY,
                base_url=config.OPENAI_RAG_MODEL_API_BASE
            )
            
            response = await client.chat.completions.create(
                model=config.OPENAI_RAG_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            response_data = json.loads(json_str)
            
            # Convert response to structured models
            filters_data = response_data.get('filters', {})
            
            # Convert numeric filters to NumericFilter objects
            for field in ['fees', 'avg_package', 'ranking']:
                if field in filters_data and isinstance(filters_data[field], dict):
                    numeric_data = filters_data[field]
                    filters_data[field] = NumericFilter(
                        value=numeric_data['value'],
                        operator=ComparisonOperator(numeric_data['operator'])
                    )
            
            # Convert college_type to enum
            if 'college_type' in filters_data:
                filters_data['college_type'] = CollegeType(filters_data['college_type'])
            
            # Create CollegeFilters object
            filters = CollegeFilters(**filters_data)
            
            # Create QueryAnalysis object
            analysis = QueryAnalysis(
                original_query=query,
                filters=filters,
                cleaned_query=response_data.get('cleaned_query', query),
                intent=response_data.get('intent', 'find_colleges'),
                confidence=response_data.get('confidence', 0.7)
            )
            
            return analysis
            
        except Exception as e:
            print(f"⚠️  LLM filter extraction failed: {e}")
            # Fallback to basic analysis
            return QueryAnalysis(
                original_query=query,
                filters=CollegeFilters(),
                cleaned_query=query,
                intent="find_colleges",
                confidence=0.1
            )
    
    # Alias for the main method
    async def extract_filters(self, query: str) -> QueryAnalysis:
        """Main method for filter extraction"""
        return await self.extract_filters_simple(query)
    
    async def close(self):
        """Clean up resources"""
        if self.model_client:
            await self.model_client.close()

# Convenience function for testing
async def test_filter_extraction():
    """Test the filter extraction functionality"""
    
    agent = FilterExtractionAgent()
    await agent.initialize()
    
    test_queries = [
        "Best MBA colleges in Delhi under 10 lakhs fees",
        "Engineering colleges in Mumbai with fees < ₹2L",
        "Private colleges with ranking better than 25",
        "Government colleges with package above 8 lakhs",
        "Top medical colleges in Karnataka accepting NEET",
        "MBA colleges in Bangalore with fees between 5-10 lakhs"
    ]
    
    print("🤖 Testing LLM-powered Filter Extraction")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        
        try:
            analysis = await agent.extract_filters(query)
            
            print(f"🎯 Extracted Filters:")
            if analysis.filters.city:
                print(f"   City: {analysis.filters.city}")
            if analysis.filters.course:
                print(f"   Course: {analysis.filters.course}")
            if analysis.filters.college_type:
                print(f"   Type: {analysis.filters.college_type.value}")
            if analysis.filters.fees:
                print(f"   Fees: {analysis.filters.fees.operator} ₹{analysis.filters.fees.value:,}")
            if analysis.filters.avg_package:
                print(f"   Package: {analysis.filters.avg_package.operator} ₹{analysis.filters.avg_package.value:,}")
            if analysis.filters.ranking:
                print(f"   Ranking: {analysis.filters.ranking.operator} {analysis.filters.ranking.value}")
            
            print(f"🧹 Cleaned Query: '{analysis.cleaned_query}'")
            print(f"🎲 Confidence: {analysis.confidence:.2f}")
            print(f"📋 Summary: {analysis.filters.to_readable_summary()}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await agent.close()

if __name__ == "__main__":
    asyncio.run(test_filter_extraction())

import json
import asyncio
from typing import         try:
            # Get LLM response using the correct autogen API
            from autogen_core.messages import UserMessage
            
            user_message = UserMessage(content=query, source="user")
            response_stream = self.agent.run_stream([user_message])
            
            response = None
            async for message in response_stream:
                response = message
            
            if not response:
                raise ValueError("No response from agent")
            
            # Extract JSON from response
            response_text = response.content if hasattr(response, 'content') else str(response)m autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from filter_models import CollegeFilters, QueryAnalysis, NumericFilter, ComparisonOperator, CollegeType
from constants import config

class FilterExtractionAgent:
    """
    LLM-powered agent that extracts structured filters from natural language queries.
    """
    
    def __init__(self):
        self.model_client: Optional[OpenAIChatCompletionClient] = None
        self.agent: Optional[AssistantAgent] = None
    
    async def initialize(self):
        """Initialize the LLM client and agent"""
        # Use the same OpenAI configuration as the main RAG system
        self.model_client = OpenAIChatCompletionClient(
            model=config.OPENAI_RAG_MODEL,
            base_url=config.OPENAI_RAG_MODEL_API_BASE,
            api_key=config.OPENAI_RAG_MODEL_API_KEY,
            max_retries=config.OPENAI_MAX_RETRIES,
        )
        
        # Create agent with specialized system prompt for filter extraction
        system_prompt = self._get_system_prompt()
        
        self.agent = AssistantAgent(
            name="filter_extraction_agent",
            model_client=self.model_client,
            system_message=system_prompt
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for filter extraction"""
        return """You are an expert at extracting structured college search filters from natural language queries.

Your task is to analyze user queries about colleges and extract specific filter criteria into a structured JSON format.

**Supported Filters:**
- city: String (e.g., "Mumbai", "Delhi", "Bangalore")
- state: String (e.g., "Maharashtra", "Karnataka") 
- fees: Numeric with operator (lt/lte/gt/gte/eq) and value in actual rupees
- avg_package: Numeric with operator and value in actual rupees
- ranking: Numeric with operator and value (lower numbers = better ranking)
- course: String (e.g., "MBA", "ENGINEERING", "MEDICAL")
- college_type: Enum ("Private", "Govt")
- exam: String (e.g., "CAT", "JEE", "NEET")

**Important Rules:**
1. Convert lakhs to actual amounts (5 lakhs = 500000)
2. For ranking: "better than 30" means ranking < 30 (operator: "lt")
3. For fees: "under 10 lakhs" means fees < 1000000 (operator: "lt")
4. Normalize college types: government/govt/public → "Govt", private → "Private"
5. Extract city names from phrases like "in Mumbai", "Delhi colleges"
6. Remove filter terms from cleaned_query but keep intent words

**Output Format:**
Always respond with valid JSON containing:
- filters: Object with extracted filters
- cleaned_query: String with filter terms removed
- intent: String describing the primary intent
- confidence: Float between 0.0-1.0

**Examples:**

Query: "Best MBA colleges in Delhi under 10 lakhs fees"
```json
{
  "filters": {
    "city": "Delhi",
    "course": "MBA", 
    "fees": {"value": 1000000, "operator": "lt"}
  },
  "cleaned_query": "best colleges",
  "intent": "find_colleges",
  "confidence": 0.9
}
```

Query: "Private engineering colleges in Mumbai with ranking better than 25"
```json
{
  "filters": {
    "city": "Mumbai",
    "course": "ENGINEERING",
    "college_type": "Private",
    "ranking": {"value": 25, "operator": "lt"}
  },
  "cleaned_query": "colleges",
  "intent": "find_colleges", 
  "confidence": 0.95
}
```

Query: "Government colleges with package above 8 lakhs"
```json
{
  "filters": {
    "college_type": "Govt",
    "avg_package": {"value": 800000, "operator": "gt"}
  },
  "cleaned_query": "colleges",
  "intent": "find_colleges",
  "confidence": 0.85
}
```

Analyze the following query and extract filters in the exact JSON format shown above:"""

    async def extract_filters(self, query: str) -> QueryAnalysis:
        """
        Extract structured filters from a natural language query using LLM.
        
        Args:
            query: Natural language query about colleges
            
        Returns:
            QueryAnalysis: Structured analysis with extracted filters
        """
        if not self.agent:
            raise ValueError("Filter extraction agent not initialized. Call initialize() first.")
        
        try:
            # Get LLM response - use run_stream and get the last message
            response_stream = self.agent.run_stream(query)
            response = None
            async for message in response_stream:
                response = message
            
            if not response:
                raise ValueError("No response from agent")
            
            # Extract JSON from response
            response_text = response.message.content if hasattr(response.message, 'content') else str(response.message)
            
            # Parse JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            response_data = json.loads(json_str)
            
            # Convert response to structured models
            filters_data = response_data.get('filters', {})
            
            # Convert numeric filters to NumericFilter objects
            for field in ['fees', 'avg_package', 'ranking']:
                if field in filters_data and isinstance(filters_data[field], dict):
                    numeric_data = filters_data[field]
                    filters_data[field] = NumericFilter(
                        value=numeric_data['value'],
                        operator=ComparisonOperator(numeric_data['operator'])
                    )
            
            # Convert college_type to enum
            if 'college_type' in filters_data:
                filters_data['college_type'] = CollegeType(filters_data['college_type'])
            
            # Create CollegeFilters object
            filters = CollegeFilters(**filters_data)
            
            # Create QueryAnalysis object
            analysis = QueryAnalysis(
                original_query=query,
                filters=filters,
                cleaned_query=response_data.get('cleaned_query', query),
                intent=response_data.get('intent', 'find_colleges'),
                confidence=response_data.get('confidence', 0.7)
            )
            
            return analysis
            
        except Exception as e:
            print(f"⚠️  LLM filter extraction failed: {e}")
            # Fallback to basic analysis
            return QueryAnalysis(
                original_query=query,
                filters=CollegeFilters(),
                cleaned_query=query,
                intent="find_colleges",
                confidence=0.1
            )
    
    async def close(self):
        """Clean up resources"""
        if self.model_client:
            await self.model_client.close()

# Convenience function for testing
async def test_filter_extraction():
    """Test the filter extraction functionality"""
    
    agent = FilterExtractionAgent()
    await agent.initialize()
    
    test_queries = [
        "Best MBA colleges in Delhi under 10 lakhs fees",
        "Engineering colleges in Mumbai with fees < ₹2L",
        "Private colleges with ranking better than 25",
        "Government colleges with package above 8 lakhs",
        "Top medical colleges in Karnataka accepting NEET",
        "MBA colleges in Bangalore with fees between 5-10 lakhs"
    ]
    
    print("🤖 Testing LLM-powered Filter Extraction")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        
        try:
            analysis = await agent.extract_filters(query)
            
            print(f"🎯 Extracted Filters:")
            if analysis.filters.city:
                print(f"   City: {analysis.filters.city}")
            if analysis.filters.course:
                print(f"   Course: {analysis.filters.course}")
            if analysis.filters.college_type:
                print(f"   Type: {analysis.filters.college_type.value}")
            if analysis.filters.fees:
                print(f"   Fees: {analysis.filters.fees.operator} ₹{analysis.filters.fees.value:,}")
            if analysis.filters.avg_package:
                print(f"   Package: {analysis.filters.avg_package.operator} ₹{analysis.filters.avg_package.value:,}")
            if analysis.filters.ranking:
                print(f"   Ranking: {analysis.filters.ranking.operator} {analysis.filters.ranking.value}")
            
            print(f"🧹 Cleaned Query: '{analysis.cleaned_query}'")
            print(f"🎲 Confidence: {analysis.confidence:.2f}")
            print(f"📋 Summary: {analysis.filters.to_readable_summary()}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await agent.close()

if __name__ == "__main__":
    asyncio.run(test_filter_extraction())
