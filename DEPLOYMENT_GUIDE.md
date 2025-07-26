# 🚀 Smart Campus Guide - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying your Smart Campus Guide application online using various platforms.

## 📋 Pre-Deployment Checklist

### 1. Required Files (✅ Already Created)
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `Procfile` - Heroku process configuration
- `railway.toml` - Railway deployment configuration
- `render.yaml` - Render deployment configuration
- `.streamlit/config.toml` - Streamlit configuration

### 2. Environment Variables Required
```bash
OPENAI_RAG_MODEL_API_KEY=your_openai_api_key_here
API_BASE_URL=your_api_endpoint_url
OPENAI_RAG_MODEL=gpt-4o
RAG_K=3
RAG_SCORE_THRESHOLD=0.3
```

## 🎯 Deployment Options

### Option 1: Streamlit Community Cloud (FREE & EASIEST)

**Best for**: Quick deployment, testing, demos

#### Steps:
1. **Generate requirements.txt from uv** (if deploying to Streamlit Cloud):
   ```bash
   uv export --format requirements-txt --output-file requirements.txt
   ```

2. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

3. **Deploy on Streamlit Cloud**:
   - Visit: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `smart-campus-guide`
   - Choose main file: `streamlit_app.py`
   - Advanced settings → Add secrets:
     ```toml
     OPENAI_RAG_MODEL_API_KEY = "your_api_key_here"
     API_BASE_URL = "your_backend_url_or_localhost"
     ```

3. **Deploy**: Click "Deploy!"

**Limitations**: 
- Only frontend deployment
- Need separate backend deployment
- 1GB memory limit

### Option 2: Railway (RECOMMENDED FOR FULL-STACK)

**Best for**: Production deployment with both frontend and backend

#### Steps:
1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Deploy**:
   ```bash
   # In your project directory
   railway init
   railway up
   ```

3. **Set Environment Variables**:
   ```bash
   railway variables set OPENAI_RAG_MODEL_API_KEY=your_key_here
   railway variables set OPENAI_RAG_MODEL=gpt-4o
   railway variables set RAG_K=3
   ```

4. **Access**: Railway will provide a public URL

**Benefits**:
- Full-stack deployment
- Automatic HTTPS
- Easy scaling
- Built-in monitoring

### Option 3: Render (FREE TIER AVAILABLE)

**Best for**: Separate frontend/backend deployment, lightweight builds

#### Quick Setup for Lighter Deployment:
For faster builds and avoiding CUDA dependencies:
```bash
./deploy.sh render
```

#### Deploy Backend (API):
1. **Create Web Service**:
   - Go to https://render.com
   - Connect GitHub repository
   - Choose "Web Service"
   - Repository: `smart-campus-guide`
   - Build Command: `pip install uv && uv sync --frozen --no-dev`
   - Start Command: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Set Environment Variables**:
   ```
   OPENAI_RAG_MODEL_API_KEY=your_key_here
   OPENAI_RAG_MODEL=gpt-3.5-turbo
   RAG_K=3
   RAG_SCORE_THRESHOLD=0.3
   ```

#### Deploy Frontend (Streamlit):
1. **Create Another Web Service**:
   - Build Command: `pip install uv && uv sync --frozen --no-dev`
   - Start Command: `uv run streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=$PORT`

2. **Set Environment Variables**:
   ```
   API_BASE_URL=https://your-api-service.onrender.com
   ```

#### Troubleshooting Render Port Issues:
- **Port Detection**: Render automatically provides `$PORT` environment variable
- **No Manual Port Setting**: Don't set PORT as an environment variable
- **Binding Issue**: Ensure your app uses `--port $PORT` in start command
- **Health Check**: Render scans for open ports automatically

### Option 4: Heroku

**Best for**: Traditional cloud deployment

#### Steps:
1. **Install Heroku CLI**:
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   
   # Set environment variables
   heroku config:set OPENAI_RAG_MODEL_API_KEY=your_key_here
   heroku config:set API_BASE_URL=https://your-api-app.herokuapp.com
   
   # Deploy
   git push heroku main
   ```

### Option 5: Google Cloud Platform

#### Steps:
1. **Install Google Cloud SDK**
2. **Deploy using Cloud Run**:
   ```bash
   gcloud run deploy smart-campus-guide \
     --image gcr.io/PROJECT_ID/smart-campus-guide \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## 🔧 Configuration for Production

### Update API Base URL
The app automatically detects the environment using the `API_BASE_URL` environment variable.

### Optimize for Production
```bash
# Reduce costs and improve performance
OPENAI_RAG_MODEL=gpt-4o  # Instead of gpt-4o
RAG_K=3                         # Reduce number of results
RAG_SCORE_THRESHOLD=0.3         # Higher threshold for relevance
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check `requirements.txt` includes all dependencies
   - Verify Python version compatibility

2. **API Connection Issues**:
   - Ensure `API_BASE_URL` environment variable is set correctly
   - Check CORS settings in FastAPI

3. **OpenAI API Errors**:
   - Verify API key is valid
   - Check API usage limits
   - Ensure sufficient account credits

4. **Memory Issues**:
   - Reduce `RAG_K` value
   - Use lighter OpenAI models
   - Implement query caching

### Logs and Monitoring:
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Render
# Check logs in dashboard

# Streamlit Cloud
# Check logs in app dashboard
```

## 🎯 Recommended Deployment Strategy

### For Development/Testing:
1. **Streamlit Community Cloud** for frontend
2. **Render** free tier for backend

### For Production:
1. **Railway** for full-stack deployment
2. **Google Cloud Platform** or **AWS** for enterprise

### For Cost Optimization:
1. Use `gpt-4o` instead of `gpt-4o`
2. Implement query caching
3. Set reasonable rate limits
4. Monitor usage regularly

## 🔐 Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** (automatic on most platforms)
4. **Implement rate limiting** for production
5. **Monitor API usage** to prevent abuse

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review platform-specific documentation
3. Check application logs
4. Verify environment variables

---

**Good luck with your deployment! 🚀**
