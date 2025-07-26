#!/usr/bin/env python3
"""
Streamlit Frontend for Smart Campus Guide - College Recommendation System
Provides a user-friendly web interface for the FastAPI backend.
"""

import streamlit as st
import requests
import time
from typing import Dict, Any, List

# Configure page
st.set_page_config(
    page_title="Smart Campus Guide",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")  # FastAPI server address
TIMEOUT = 30  # Request timeout in seconds

# CSS for custom styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .recommendation-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


class APIClient:
    """Client for interacting with the FastAPI backend."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def check_health(self) -> Dict[str, Any]:
        """Check API health status."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=TIMEOUT)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        try:
            response = requests.get(f"{self.base_url}/config", timeout=TIMEOUT)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_recommendations(self, query: str, include_analysis: bool = False) -> Dict[str, Any]:
        """Get college recommendations."""
        try:
            payload = {
                "query": query,
                "include_analysis": include_analysis
            }
            response = requests.post(
                f"{self.base_url}/recommend",
                json=payload,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_batch_recommendations(self, queries: List[str]) -> Dict[str, Any]:
        """Get batch recommendations."""
        try:
            response = requests.post(
                f"{self.base_url}/recommend/batch",
                json=queries,
                timeout=TIMEOUT * 2  # Longer timeout for batch processing
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}


# Initialize API client
@st.cache_resource
def get_api_client():
    return APIClient(API_BASE_URL)


def show_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Smart Campus Guide</h1>
        <p>AI-Powered College Recommendation System</p>
        <p>Find your perfect college match with intelligent search and personalized recommendations</p>
    </div>
    """, unsafe_allow_html=True)


def show_sidebar():
    """Display the sidebar with navigation and information."""
    st.sidebar.title("🚀 Navigation")
    
    # Navigation
    pages = ["🏠 Home", "🔍 Search Colleges", "📊 Batch Analysis", "⚙️ System Status", "📚 Help & Examples"]
    current_page = st.session_state.get('page', "🏠 Home")
    
    # Ensure current page is in the list
    if current_page not in pages:
        current_page = "🏠 Home"
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        pages,
        index=pages.index(current_page),
        key="navigation_selectbox"
    )
    
    st.sidebar.markdown("---")
    
    # Quick stats
    st.sidebar.title("📈 Quick Stats")
    api_client = get_api_client()
    
    with st.sidebar:
        # API Health Check
        health_status = api_client.check_health()
        if health_status["success"]:
            st.success("✅ API Online")
            if "rag_system_initialized" in health_status["data"]:
                if health_status["data"]["rag_system_initialized"]:
                    st.success("✅ RAG System Ready")
                else:
                    st.warning("⚠️ RAG System Initializing...")
        else:
            st.error("❌ API Offline")
        
        # System Configuration
        config_result = api_client.get_config()
        if config_result["success"]:
            config_data = config_result["data"]
            st.metric("RAG K", config_data.get("rag_k", "N/A"))
            st.metric("Score Threshold", config_data.get("score_threshold", "N/A"))
    
    st.sidebar.markdown("---")
    
    # Tips
    st.sidebar.title("💡 Quick Tips")
    st.sidebar.markdown("""
    **Example Queries:**
    - "MBA colleges in Delhi under 10 lakhs"
    - "Best engineering colleges in Mumbai"
    - "Private medical colleges with good placement"
    - "Law colleges with fees under 5 lakhs"
    
    **Search Tips:**
    - Be specific about location, course, and budget
    - Mention college type (private/government)
    - Include ranking or placement preferences
    """)
    
    return page


def show_home_page():
    """Display the home page."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered Search</h3>
            <p>Natural language queries with intelligent understanding of your preferences and requirements.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Smart Filtering</h3>
            <p>Advanced filtering by location, fees, rankings, courses, and college type for precise results.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Comprehensive Data</h3>
            <p>Access to detailed college information including fees, placements, rankings, and more.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick search section
    st.markdown("## 🚀 Quick Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        quick_query = st.text_input(
            "What kind of college are you looking for?",
            placeholder="e.g., MBA colleges in Mumbai under 8 lakhs",
            key="quick_search"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary", key="quick_search_btn")
    
    if search_button and quick_query:
        st.session_state['current_query'] = quick_query
        st.session_state['page'] = "🔍 Search Colleges"
        st.rerun()
    
    # Recent queries
    if 'query_history' in st.session_state and st.session_state.query_history:
        st.markdown("## 📝 Recent Searches")
        for i, query in enumerate(st.session_state.query_history[-3:]):
            if st.button(f"🔄 {query}", key=f"recent_{i}"):
                st.session_state['current_query'] = query
                st.session_state['page'] = "🔍 Search Colleges"
                st.rerun()


def show_search_page():
    """Display the main search page."""
    st.markdown("## 🔍 College Search")
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            query = st.text_area(
                "Enter your college search query:",
                value=st.session_state.get('current_query', ''),
                placeholder="e.g., Engineering colleges in Bangalore with fees under 3 lakhs and good placements",
                height=100,
                help="Be specific about your requirements for better results"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            include_analysis = st.checkbox("Include Analysis", help="Show query analysis details")
            submit_button = st.form_submit_button("🎯 Get Recommendations", type="primary")
    
    if submit_button and query:
        # Add to query history
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        if query not in st.session_state.query_history:
            st.session_state.query_history.append(query)
            # Keep only last 10 queries
            st.session_state.query_history = st.session_state.query_history[-10:]
        
        # Show loading spinner
        with st.spinner("🤖 Analyzing your query and finding the best colleges..."):
            api_client = get_api_client()
            result = api_client.get_recommendations(query, include_analysis)
        
        if result["success"]:
            data = result["data"]
            
            # Success message
            st.markdown("""
            <div class="success-message">
                ✅ Successfully found college recommendations!
            </div>
            """, unsafe_allow_html=True)
            
            # Display recommendations
            st.markdown("### 🎓 Recommended Colleges")
            st.markdown("""
            <div class="recommendation-card">
            """ + data["recommendations"].replace("\n", "<br>") + """
            </div>
            """, unsafe_allow_html=True)
            
            # Show analysis if requested
            if include_analysis and data.get("analysis"):
                with st.expander("🔍 Query Analysis Details"):
                    st.json(data["analysis"])
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Search Again"):
                    st.session_state['current_query'] = ""
                    st.rerun()
            with col2:
                if st.button("📋 Copy Results"):
                    st.text_area("Copy this text:", data["recommendations"], height=100)
            with col3:
                if st.button("📤 Share Query"):
                    st.info(f"Share this query: {query}")
        
        else:
            st.markdown(f"""
            <div class="error-message">
                ❌ Error: {result['error']}
            </div>
            """, unsafe_allow_html=True)
            
            st.error("Please check if the API server is running and try again.")


def show_batch_analysis_page():
    """Display the batch analysis page."""
    st.markdown("## 📊 Batch Analysis")
    st.markdown("Analyze multiple queries at once to compare different college options.")
    
    # Batch query input
    st.markdown("### 📝 Enter Multiple Queries")
    
    # Predefined query templates
    with st.expander("📋 Use Query Templates"):
        templates = [
            "MBA colleges in Delhi under 10 lakhs",
            "Engineering colleges in Mumbai with good placements",
            "Medical colleges in Bangalore under 15 lakhs",
            "Law colleges in Chennai with fees under 5 lakhs",
            "Computer Science colleges in Pune under 8 lakhs"
        ]
        
        selected_templates = []
        for template in templates:
            if st.checkbox(template, key=f"template_{template}"):
                selected_templates.append(template)
        
        if st.button("Add Selected Templates") and selected_templates:
            if 'batch_queries' not in st.session_state:
                st.session_state.batch_queries = []
            st.session_state.batch_queries.extend(selected_templates)
            st.success(f"Added {len(selected_templates)} templates!")
    
    # Manual query entry
    col1, col2 = st.columns([4, 1])
    
    with col1:
        new_query = st.text_input("Add a query:", placeholder="e.g., MBA colleges in Hyderabad")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("➕ Add Query") and new_query:
            if 'batch_queries' not in st.session_state:
                st.session_state.batch_queries = []
            st.session_state.batch_queries.append(new_query)
            st.success("Query added!")
    
    # Display current queries
    if 'batch_queries' in st.session_state and st.session_state.batch_queries:
        st.markdown("### 📋 Current Queries")
        
        for i, query in enumerate(st.session_state.batch_queries):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"{i+1}. {query}")
            with col2:
                if st.button("🗑️", key=f"delete_{i}", help="Remove query"):
                    st.session_state.batch_queries.pop(i)
                    st.rerun()
        
        # Analyze batch
        if st.button("🚀 Analyze All Queries", type="primary"):
            if len(st.session_state.batch_queries) > 10:
                st.error("Maximum 10 queries allowed for batch processing.")
            else:
                with st.spinner("🤖 Processing all queries... This may take a moment."):
                    api_client = get_api_client()
                    result = api_client.get_batch_recommendations(st.session_state.batch_queries)
                
                if result["success"]:
                    data = result["data"]
                    
                    st.success(f"✅ Successfully processed {data['total_processed']} queries!")
                    
                    # Display results
                    for i, result_item in enumerate(data["results"]):
                        with st.expander(f"📊 Results for: {result_item['query']}"):
                            recommendations_html = result_item['recommendations'].replace('\n', '<br>')
                            st.markdown(f"""
                            <div class="recommendation-card">
                            {recommendations_html}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Summary statistics
                    st.markdown("### 📈 Batch Analysis Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Queries", len(st.session_state.batch_queries))
                    with col2:
                        st.metric("Processed Successfully", data['total_processed'])
                    with col3:
                        st.metric("Success Rate", f"{(data['total_processed']/len(st.session_state.batch_queries)*100):.1f}%")
                
                else:
                    st.error(f"❌ Batch processing failed: {result['error']}")
        
        # Clear all queries
        if st.button("🗑️ Clear All Queries"):
            st.session_state.batch_queries = []
            st.success("All queries cleared!")
    else:
        st.info("📝 Add some queries above to start batch analysis.")


def show_system_status_page():
    """Display the system status page."""
    st.markdown("## ⚙️ System Status")
    
    api_client = get_api_client()
    
    # Health check
    st.markdown("### 🏥 Health Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)", key="auto_refresh")
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # API Health
    health_result = api_client.check_health()
    
    if health_result["success"]:
        health_data = health_result["data"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>✅ API Status</h3>
                <p>Healthy</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            rag_status = "✅ Ready" if health_data.get("rag_system_initialized", False) else "⚠️ Initializing"
            st.markdown(f"""
            <div class="metric-card">
                <h3>🤖 RAG System</h3>
                <p>{rag_status}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Version</h3>
                <p>{health_data.get('version', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed health information
        with st.expander("🔍 Detailed Health Information"):
            st.json(health_data)
    
    else:
        st.markdown("""
        <div class="error-message">
            ❌ API Health Check Failed<br>
            Error: """ + str(health_result.get('error', 'Unknown error')) + """
        </div>
        """, unsafe_allow_html=True)
    
    # Configuration
    st.markdown("### ⚙️ System Configuration")
    
    config_result = api_client.get_config()
    
    if config_result["success"]:
        config_data = config_result["data"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**RAG Configuration:**")
            st.write(f"• K (Top Results): {config_data.get('rag_k', 'N/A')}")
            st.write(f"• Score Threshold: {config_data.get('score_threshold', 'N/A')}")
            st.write(f"• Chunk Size: {config_data.get('chunk_size', 'N/A')}")
        
        with col2:
            st.markdown("**Model Configuration:**")
            st.write(f"• Embedding Model: {config_data.get('embedding_model', 'N/A')}")
            st.write(f"• OpenAI Model: {config_data.get('openai_model', 'N/A')}")
            st.write(f"• Collection: {config_data.get('collection_name', 'N/A')}")
        
        with st.expander("🔍 Full Configuration"):
            st.json(config_data)
    
    else:
        st.error(f"❌ Failed to fetch configuration: {config_result.get('error', 'Unknown error')}")
    
    # Performance metrics (if available)
    st.markdown("### 📈 Performance Metrics")
    
    if 'query_history' in st.session_state:
        total_queries = len(st.session_state.query_history)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Queries", total_queries)
        
        with col2:
            st.metric("Session Duration", f"{time.time() - st.session_state.get('session_start', time.time()):.0f}s")
        
        with col3:
            avg_queries = total_queries / max(1, (time.time() - st.session_state.get('session_start', time.time())) / 60)
            st.metric("Queries/Min", f"{avg_queries:.1f}")


def show_help_page():
    """Display the help and examples page."""
    st.markdown("## 📚 Help & Examples")
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start Guide")
    
    with st.expander("1. 🔍 Basic Search"):
        st.markdown("""
        **How to search for colleges:**
        1. Go to the "Search Colleges" page
        2. Enter your query in natural language
        3. Click "Get Recommendations"
        4. Review the results and refine if needed
        
        **Example:** "MBA colleges in Delhi under 10 lakhs"
        """)
    
    with st.expander("2. 📊 Batch Analysis"):
        st.markdown("""
        **How to compare multiple options:**
        1. Go to the "Batch Analysis" page
        2. Add multiple queries using templates or manual entry
        3. Click "Analyze All Queries"
        4. Compare results across different searches
        
        **Use case:** Compare MBA programs across different cities
        """)
    
    with st.expander("3. ⚙️ System Monitoring"):
        st.markdown("""
        **How to check system status:**
        1. Go to the "System Status" page
        2. View API health and RAG system status
        3. Check configuration settings
        4. Monitor performance metrics
        """)
    
    # Query examples
    st.markdown("### 💡 Example Queries")
    
    examples = {
        "🎓 Course-based Searches": [
            "MBA colleges in Mumbai with good placements",
            "Engineering colleges in Bangalore under 5 lakhs",
            "Medical colleges in Delhi with NEET acceptance",
            "Law colleges in Chennai with moot court facilities"
        ],
        "💰 Budget-based Searches": [
            "Private colleges under 3 lakhs fees",
            "Engineering colleges with fees between 2-5 lakhs",
            "MBA programs under 10 lakhs in tier-1 cities",
            "Affordable government colleges in Maharashtra"
        ],
        "🏆 Ranking-based Searches": [
            "Top 20 engineering colleges in India",
            "Highly ranked business schools in Bangalore",
            "Government colleges with good rankings",
            "Private colleges with excellent placement records"
        ],
        "📍 Location-based Searches": [
            "Colleges in NCR region for computer science",
            "Best colleges in South India for biotechnology",
            "Engineering colleges in tier-2 cities",
            "Colleges near Mumbai with hostel facilities"
        ]
    }
    
    for category, queries in examples.items():
        with st.expander(category):
            for query in queries:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {query}")
                with col2:
                    if st.button("Try", key=f"try_{query}", help="Try this query"):
                        st.session_state['current_query'] = query
                        st.session_state['page'] = "🔍 Search Colleges"
                        st.rerun()
    
    # Tips and best practices
    st.markdown("### 💡 Tips for Better Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Be Specific:**
        - Include location (city/state)
        - Mention course/program
        - Specify budget range
        - Include college type preference
        
        **✅ Good:** "Private MBA colleges in Mumbai under 8 lakhs"
        **❌ Avoid:** "Good colleges"
        """)
    
    with col2:
        st.markdown("""
        **🔍 Use Keywords:**
        - Fees, budget, cost
        - Placements, packages
        - Rankings, ratings
        - Facilities, infrastructure
        
        **✅ Good:** "Engineering colleges with placement above 80%"
        **❌ Avoid:** "Nice engineering colleges"
        """)
    
    # FAQ
    st.markdown("### ❓ Frequently Asked Questions")
    
    faqs = {
        "How accurate are the recommendations?": "The system uses advanced AI to understand your query and match it with relevant colleges from our comprehensive database. Results are based on the latest available data.",
        "Can I search for specific courses?": "Yes! You can search for any course like MBA, Engineering, Medical, Law, etc. Be specific about the specialization for better results.",
        "What if I don't get relevant results?": "Try rephrasing your query with more specific details like location, budget, or course. You can also use the example queries as templates.",
        "Is the fee information up to date?": "We strive to maintain current fee information, but please verify directly with the colleges for the most accurate and up-to-date fees.",
        "Can I compare colleges?": "Yes! Use the Batch Analysis feature to compare multiple queries and find the best options across different criteria."
    }
    
    for question, answer in faqs.items():
        with st.expander(question):
            st.write(answer)
    
    # Contact and support
    st.markdown("### 📞 Support & Contact")
    
    st.info("""
    **Need Help?**
    - Check the System Status page for any service issues
    - Try the example queries to understand the format
    - Use specific keywords for better search results
    - Ensure the FastAPI server is running on localhost:8001
    """)


def main():
    """Main application function."""
    # Initialize session state
    if 'session_start' not in st.session_state:
        st.session_state.session_start = time.time()
    
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Home"
    
    # Show header
    show_header()
    
    # Show sidebar and get selected page
    selected_page = show_sidebar()
    
    # Update page in session state (give priority to session state changes from widgets)
    st.session_state.page = selected_page
    
    # Display the selected page
    if st.session_state.page == "🏠 Home":
        show_home_page()
    elif st.session_state.page == "🔍 Search Colleges":
        show_search_page()
    elif st.session_state.page == "📊 Batch Analysis":
        show_batch_analysis_page()
    elif st.session_state.page == "⚙️ System Status":
        show_system_status_page()
    elif st.session_state.page == "📚 Help & Examples":
        show_help_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🎓 Smart Campus Guide - Powered by AI & RAG Technology</p>
        <p>Built with Streamlit & FastAPI | © 2025</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
