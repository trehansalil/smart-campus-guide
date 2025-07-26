FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install uv
RUN pip install uv

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8001 8501

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Smart Campus Guide..."\n\
echo "🔧 Starting FastAPI backend..."\n\
python main.py &\n\
echo "🎨 Starting Streamlit frontend..."\n\
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]
