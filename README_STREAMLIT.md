# Streamlit Frontend for Smart Campus Guide

This directory contains the Streamlit-based web interface for the Smart Campus Guide college recommendation system.

## 🎨 Features

### 🏠 Home Page
- Quick search functionality
- Feature overview cards
- Recent search history
- Getting started guide

### 🔍 Search Colleges
- Natural language query input
- Real-time recommendations
- Query analysis details (optional)
- Copy and share functionality

### 📊 Batch Analysis
- Compare multiple queries simultaneously
- Pre-defined query templates
- Batch processing with progress tracking
- Summary statistics and metrics

### ⚙️ System Status
- Real-time API health monitoring
- RAG system status
- Configuration details
- Performance metrics

### 📚 Help & Examples
- Comprehensive query examples
- Best practices for searching
- FAQ section
- Category-based example templates

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- FastAPI backend running on `http://localhost:8001`
- All dependencies installed (see requirements below)

### Installation

1. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv install

   # Or install specific packages with pip (if needed)
   pip install streamlit plotly requests pandas
   ```

2. **Ensure FastAPI backend is running:**
   ```bash
   # Start the FastAPI server first
   uv run python main.py
   ```

3. **Start Streamlit app:**
   ```bash
   uv run streamlit run streamlit_app.py
   ```

4. **Access the application:**
   - Open your browser to `http://localhost:8501`

### Using the Startup Script (Recommended)

The included `start_app.sh` script can start both backend and frontend automatically:

```bash
# Start full stack (FastAPI + Streamlit)
./start_app.sh

# Or start components individually
./start_app.sh api        # Start only FastAPI
./start_app.sh frontend   # Start only Streamlit
./start_app.sh status     # Check service status
./start_app.sh stop       # Stop all services
```

## 📁 File Structure

```
├── streamlit_app.py      # Main Streamlit application
├── start_app.sh          # Startup script for full stack
└── README_STREAMLIT.md   # This documentation
```

## 🎯 Usage Guide

### Basic Search
1. Navigate to "Search Colleges" page
2. Enter your query in natural language
3. Click "Get Recommendations"
4. Review results and refine if needed

**Example queries:**
- "MBA colleges in Delhi under 10 lakhs"
- "Engineering colleges in Mumbai with good placements"
- "Private medical colleges in Bangalore"

### Batch Analysis
1. Go to "Batch Analysis" page
2. Add multiple queries using templates or manual entry
3. Click "Analyze All Queries"
4. Compare results across different searches

**Use cases:**
- Compare programs across different cities
- Evaluate options within budget ranges
- Analyze course availability across regions

### System Monitoring
1. Visit "System Status" page
2. Check API and RAG system health
3. Monitor configuration settings
4. View performance metrics

## 🔧 Configuration

### API Configuration
The app connects to your FastAPI backend. Update these settings in `streamlit_app.py` if needed:

```python
# API Configuration
API_BASE_URL = "http://localhost:8001"  # FastAPI server address
TIMEOUT = 30  # Request timeout in seconds
```

### Streamlit Configuration
Create a `.streamlit/config.toml` file for custom settings:

```toml
[server]
address = "0.0.0.0"
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 🎨 Customization

### Styling
The app uses custom CSS for styling. Modify the CSS in the `st.markdown()` sections to customize:

- Color schemes
- Card layouts
- Typography
- Spacing and margins

### Adding Features
The modular design makes it easy to add new features:

1. **Add new pages:** Create new functions like `show_new_page()`
2. **Extend API client:** Add methods to `APIClient` class
3. **Custom components:** Use Streamlit components for advanced UI

### Example: Adding a New Page

```python
def show_my_new_page():
    """Display a custom page."""
    st.markdown("## 🆕 My New Feature")
    # Your custom content here

# Add to main navigation
def show_sidebar():
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "🔍 Search", "🆕 My New Feature"]  # Add here
    )
    return page

# Handle in main function
def main():
    if st.session_state.page == "🆕 My New Feature":
        show_my_new_page()
```

## 🐛 Troubleshooting

### Common Issues

1. **"Connection refused" errors:**
   - Ensure FastAPI backend is running on port 8001
   - Check if the API server is healthy: `curl http://localhost:8001/health`

2. **Import errors:**
   - Install missing dependencies: `uv install` or `pip install streamlit plotly requests`
   - Ensure you're in the correct virtual environment

3. **Page not loading:**
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Restart Streamlit: `Ctrl+C` then `uv run streamlit run streamlit_app.py`

4. **Slow performance:**
   - Check API response times
   - Monitor system resources
   - Consider reducing batch query sizes

### Debug Mode

Enable debug mode for more detailed error information:

```bash
uv run streamlit run streamlit_app.py --logger.level=debug
```

### Checking Logs

- **Streamlit logs:** Displayed in terminal where you started the app
- **FastAPI logs:** Check `fastapi.log` file (if using startup script)
- **Browser console:** Press F12 and check console tab

## 🔒 Security Considerations

### Production Deployment

When deploying to production:

1. **Update API URL:** Change `API_BASE_URL` to your production FastAPI server
2. **Enable authentication:** Add user authentication if needed
3. **Use HTTPS:** Ensure both frontend and backend use HTTPS
4. **Configure CORS:** Set appropriate CORS policies on the FastAPI backend

### Environment Variables

Consider using environment variables for configuration:

```python
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
```

## 📊 Performance Optimization

### Caching
The app uses Streamlit's caching features:

```python
@st.cache_resource
def get_api_client():
    return APIClient(API_BASE_URL)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_config():
    return api_client.get_config()
```

### Best Practices
- Use session state for user preferences
- Implement pagination for large result sets
- Add loading spinners for long operations
- Optimize API calls with appropriate timeouts

## 🚀 Deployment Options

### Local Development
```bash
uv run streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501
```

### Docker Deployment
Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY streamlit_app.py .
COPY .streamlit/ .streamlit/

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
```

### Cloud Deployment
- **Streamlit Cloud:** Deploy directly from GitHub
- **Heroku:** Use the Heroku Streamlit buildpack
- **AWS/GCP/Azure:** Deploy using container services

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify FastAPI backend is running and healthy
3. Review the logs for error messages
4. Ensure all dependencies are properly installed

## 🛠️ Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes in `streamlit_app.py`
3. Test thoroughly with different queries
4. Update documentation
5. Submit pull request

### Testing
- Test all pages and functionality
- Verify API integration works correctly
- Check responsive design on different screen sizes
- Test error handling with invalid inputs

---

**Happy coding! 🎓✨**
