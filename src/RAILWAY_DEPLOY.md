# 🚀 Railway Deployment Guide

This guide will help you deploy the RAG Application to [Railway](https://railway.app).

## Prerequisites

1. A [Railway account](https://railway.app) (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. The following API keys ready:
   - **Supabase**: URL and API Key
   - **OpenRouter**: API Key (for LLM generation)
   - **Gemini**: API Key (for embeddings)
   - **Qdrant Cloud**: URL and API Key

---

## Step 1: Prepare Your Repository

Make sure these files exist in your `src` folder (already created):

```
src/
├── Procfile           # Tells Railway how to start the app
├── railway.json       # Railway configuration
├── runtime.txt        # Python version specification
├── requirements.txt   # Python dependencies
└── main.py           # Your FastAPI application
```

**Important**: Ensure `.env` is in `.gitignore` (it already is) - never commit secrets!

---

## Step 2: Deploy to Railway

### Option A: Deploy via GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Go to [Railway Dashboard](https://railway.app/dashboard)**

3. **Click "New Project" → "Deploy from GitHub repo"**

4. **Select your repository** and authorize Railway if needed

5. **Choose the `src` folder as root directory**:
   - Go to **Settings** → **Root Directory**
   - Set it to: `src`

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize and deploy**
   ```bash
   cd src
   railway init
   railway up
   ```

---

## Step 3: Configure Environment Variables

In Railway Dashboard, go to your project → **Variables** tab and add:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon/service key | `eyJhbGc...` |
| `SUPABASE_BUCKET` | Storage bucket name | `rag-files` |
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-v1-...` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `QDRANT_URL` | Qdrant Cloud URL | `https://xxxxx.qdrant.io` |
| `QDRANT_API_KEY` | Qdrant API key | `...` |

### Optional Variables (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `rag_app` | Application name |
| `APP_VERSION` | `0.1` | Application version |
| `GENERATION_BACKEND` | `OPENROUTER` | LLM provider for generation |
| `EMBEDDING_BACKEND` | `GEMINI` | LLM provider for embeddings |
| `GENERATION_MODEL_ID` | `qwen/qwen3-4b:free` | OpenRouter model ID |
| `EMBEDDING_MODEL_ID` | `text-embedding-004` | Gemini embedding model |
| `EMBEDDING_MODEL_SIZE` | `768` | Embedding vector size |
| `VECTOR_DB_BACKEND` | `QDRANT` | Vector DB provider |
| `PRIMARY_LANG` | `ar` | Primary language |
| `DEFAULT_LANG` | `ar` | Default language |

---

## Step 4: Generate Public URL

1. In Railway Dashboard, go to your service
2. Click **Settings** → **Networking**
3. Click **"Generate Domain"** to get a public URL
4. Your API will be available at: `https://your-app.up.railway.app`

---

## Step 5: Test Your Deployment

Once deployed, test the health endpoint:

```bash
curl https://your-app.up.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-24T..."
}
```

---

## Troubleshooting

### Build Fails
- Check **Deploy Logs** in Railway dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### App Crashes on Startup
- Check that all required environment variables are set
- Look at **Runtime Logs** for error messages
- Ensure Supabase, Qdrant, and API keys are valid

### Connection Refused
- Verify the app is using `$PORT` (Railway provides this)
- Check that `host` is set to `0.0.0.0`

### Health Check Fails
- Increase `healthcheckTimeout` in `railway.json`
- Check if `/api/v1/health` endpoint is working

---

## Cost Estimation

Railway Free Tier includes:
- **$5 free credit** per month
- **500 hours** of usage

For a small RAG app, this is usually sufficient for development/testing.

---

## Quick Reference

| Resource | Link |
|----------|------|
| Railway Dashboard | https://railway.app/dashboard |
| Railway Docs | https://docs.railway.app |
| Your API (after deploy) | `https://your-app.up.railway.app/api/v1` |

---

## API Endpoints (After Deployment)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/data/upload/{project_id}` | POST | Upload file |
| `/api/v1/data/process/{project_id}` | POST | Process/chunk file |
| `/api/v1/nlp/index/push/{project_id}` | POST | Index to vector DB |
| `/api/v1/nlp/index/search/{project_id}` | POST | Semantic search |
| `/api/v1/nlp/index/answer/{project_id}` | POST | RAG answer |
