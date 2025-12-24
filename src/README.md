# RAG Application

A Retrieval-Augmented Generation (RAG) application built with FastAPI, using Supabase for metadata and file storage, and Qdrant Cloud for vector storage.

## 🏗️ Architecture

| Component | Service | Purpose |
|-----------|---------|---------|
| **Metadata** | Supabase (PostgreSQL) | Projects, Assets, Chunks |
| **File Storage** | Supabase Storage | Uploaded documents (PDF, TXT) |
| **Vector DB** | Qdrant Cloud | Embeddings for semantic search |
| **LLM** | Google Gemini | Embeddings + Generation |

## 📋 Prerequisites

- Python 3.10+
- Supabase account (free tier available)
- Qdrant Cloud account (free tier available)
- Google Gemini API key

## 🚀 Setup

### 1. Clone and Install Dependencies

```bash
cd src
pip install -r requirements.txt
```

### 2. Supabase Setup

1. Go to [supabase.com](https://supabase.com) and create a project
2. Get your credentials from: **Project Settings → API**
   - Project URL → `SUPABASE_URL`
   - service_role key → `SUPABASE_KEY`
3. Create the database tables:
   - Go to **SQL Editor** in Supabase Dashboard
   - Copy the content from `migrations/001_create_tables.sql`
   - Run the SQL
4. Create a storage bucket:
   - Go to **Storage** → **New Bucket**
   - Name it `rag-files`
   - Set it as **Private**

### 3. Qdrant Cloud Setup

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a new cluster (free tier available)
3. Get your credentials:
   - Cluster URL → `QDRANT_URL`
   - Create an API Key → `QDRANT_API_KEY`

### 4. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=rag-files

GEMINI_API_KEY=your-gemini-api-key

QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
```

### 5. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Endpoints

### Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/data/upload/{project_id}` | Upload a file |
| POST | `/api/v1/data/process/{project_id}` | Process files into chunks |

### NLP Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/nlp/index/push/{project_id}` | Index chunks into vector DB |
| GET | `/api/v1/nlp/index/info/{project_id}` | Get index information |
| POST | `/api/v1/nlp/index/search/{project_id}` | Search in vector DB |
| POST | `/api/v1/nlp/index/answer/{project_id}` | Get RAG answer |

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |

## 📝 Example Usage

### 1. Upload a File

```bash
curl -X POST "http://localhost:8000/api/v1/data/upload/myproject" \
  -F "file=@document.pdf"
```

### 2. Process the File

```bash
curl -X POST "http://localhost:8000/api/v1/data/process/myproject" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size": 500, "overlap": 50, "do_reset": 0}'
```

### 3. Index into Vector DB

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/index/push/myproject" \
  -H "Content-Type: application/json" \
  -d '{"do_reset": 0}'
```

### 4. Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/index/answer/myproject" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the main topic?", "limit": 5}'
```

## 📁 Project Structure

```
src/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── controllers/           # Business logic controllers
├── models/               # Pydantic models and DB schemas
├── routes/               # API route definitions
├── stores/               # External service integrations
│   ├── supabase/        # Supabase client
│   ├── vectordb/        # Qdrant integration
│   └── llm/             # LLM providers
├── helpers/              # Configuration and utilities
└── migrations/           # Database migration scripts
```

## 🔧 Supported File Types

- PDF (`.pdf`)
- Text (`.txt`)

Add more file types in `.env`:
```env
FILE_ALLOWED_TYPES = ["application/pdf", "text/plain"]
```

## 📄 License

MIT License
