# 📚 RAG Application for Educational Website

A Retrieval-Augmented Generation (RAG) system built specifically for **educational platforms**.  
The goal of this project is to ensure that students interact only with **lesson-related content**, by requiring them to upload the study material before asking any questions.  
This creates a focused, controlled, and academically reliable learning experience.

---

## 🚀 Overview

This project implements a **standard RAG pipeline** (not a chatbot yet).  
It processes any educational file uploaded by the student, extracts its content, embeds it, and answers questions strictly based on that content.

The system prevents unrelated or hallucinated answers by **forcing the student to upload a file first**, ensuring the knowledge base is always tied to the course material.

---

## ✨ Key Features

- **Mandatory Document Upload**  
  Students must upload a file (PDF, TXT, etc.) before they can ask questions.  
  This guarantees that all answers come only from the lesson content.

- **RAG Pipeline**  
  - Text extraction  
  - Chunking  
  - Embedding  
  - Semantic retrieval  
  - Context-aware answer generation  

- **FastAPI Backend**  
  Fully modular API for indexing and querying documents.

- **Clear, Maintainable Structure**  
  Organized services, routes, and utilities to support easy scaling.

- **Supports Different Document Types**  
  Extendable loaders for educational materials.

- **Suitable for Integration with Any Frontend**  
  The API returns clean JSON responses.

---

## 📁 Project Structure (High-Level)
```bash
src
│
├── assets/
│  ├── Database/ 
│  ├── files/ 
│  └── .gitignore
│ 
│
├── controllers/
│ ├── __init__py
│ ├── BaseController.py 
│ ├── ProcessController.py
│ ├── ProjectControlle.py
│ ├── DataController.py 
│ └── NLPController.py
│
├── models/
│  ├── __init__.py
│  ├── AssetModel.py
│  ├── BaseDataModel.py
│  ├── ChunkModel.py
│  ├── ProjectModel.py
│  │
│  ├── db_schemes/
│  │ ├── __init__.py
│  │ ├── asset.py
│  │ ├── data_chunk.py
│  │ └── project.py 
│  │
│  ├── enums/
│  │ ├── __init__.py
│  │ ├── AssetTypeEnum.py
│  │ ├── DataBaseEnum.py
│  │ ├── ProcessingEnums.py
│  │ └── ResponseEnums.py
│  
│
├── helpers/
│ ├── config.py # Settings, environment variables
│ └── __init__.py
│
├── routes/
│  ├── init.py
│  ├── data.py # Handles data endpoints and operations
│  ├── base.py # Base routes or shared utilities
│  ├── health.py # Health check endpoint
│  ├── nlp.py # NLP-specific endpoints (question answering, RAG)
│  ├── schemes/
│  │ ├── init.py
│  │ ├── data.py # Pydantic schemas for data
│  │ └── nlp.py
│
│
├── vectordb/
│  ├── init.py
│  ├── VectorDBEnums.py
│  ├── VectorDBInterface.py
│  ├── VectorDBProviderFactory.py
│  └── providers/
│  ├── init.py
│  └── QdrantDBProvider.py
│
├── llm/
│  ├── init.py
│  ├── LLMEnums.py
│  ├── LLMInterface.py
│  ├── LLMProviderFactory.py
│  ├── providers/
│  │ ├── init.py
│  │ ├── CoHereProvider.py
│  │ └── GeminiProvider.py
│  ├── templates/
│  │ ├── init.py
│  │ ├── Template_parser.py
│  │ ├── locales/
│  │ │ ├── ar/
│  │ │ │ ├── init.py
│  │ │ │ └── rag.py
│  │ │ ├── en/
│  │ │ │ ├── init.py
│  │ │ │ └── rag.py
│
│
├── .env 
├── .env.example
├── .gitignore
├── main.py # FastAPI entry point
└── requirements.txt
```
## Explanation

Below is a full breakdown of the project structure and the responsibility of each directory.  
The architecture follows a clean modular design to support scalability, maintainability, and clear separation of concerns.

---

### **📂 assets/**
Stores project-related static assets.

- **Database/** → Local database files or vector storage (if applicable).
- **files/** → User-uploaded lesson files used for RAG processing.
- **.gitignore** → Ensures heavy asset files are not committed.

---

### **📂 controllers/**
Contains the main business logic for handling processing, project state, and NLP operations.  
Controllers act as the middle layer between routes and models.

Files include:

- **BaseController.py** → Shared logic for all controllers.
- **ProjectController.py** → Handles project-level operations.
- **ProcessController.py** → Manages file processing (chunking, embedding).
- **DataController.py** → Handles data retrieval & storage logic.
- **NLPController.py** → Executes RAG pipeline and NLP functionalities.

---

### **📂 models/**
Includes all data structures and ORM-like models that represent system entities.

- **AssetModel.py** → Represents uploaded assets.
- **BaseDataModel.py** → Shared attributes for data models.
- **ChunkModel.py** → Represents text chunks generated during processing.
- **ProjectModel.py** → Represents a complete RAG project instance.

#### **📁 models/db_schemes/**
Pydantic/DB schemas for structured storage:

- `asset.py`
- `data_chunk.py`
- `project.py`

#### **📁 models/enums/**
Contains enums that define constant values used across the system:

- **AssetTypeEnum.py** → File types or asset categories.
- **DataBaseEnum.py** → Supported database/vector backends.
- **ProcessingEnums.py** → Status of processing pipeline.
- **ResponseEnums.py** → Standard API response codes.

---

### **📂 helpers/**
Utility and configuration helpers.

- **config.py** → Environment variables, settings loader.
- **__init__.py**

---

### **📂 routes/**
Contains all FastAPI routes that expose system functionality.

- **data.py** → Endpoints to manage assets, create projects, upload files.
- **base.py** → Base/shared routes.
- **health.py** → Health check endpoint for DevOps.
- **nlp.py** → RAG query endpoint (question answering).

#### **📁 routes/schemes/**
Request/response validation models (Pydantic):

- **data.py**
- **nlp.py**

---

### **📂 vectordb/**
Handles vector storage used for semantic search.

- **VectorDBInterface.py** → Base interface for vector DB operations.
- **VectorDBEnums.py** → Supported vector backends (Qdrant, etc.).
- **VectorDBProviderFactory.py** → Factory to return correct DB provider.

#### **📁 vectordb/providers/**
Actual vector DB implementations:

- **QdrantDBProvider.py** → Qdrant-based vector storage implementation.

---

### **📂 llm/**
Handles all interactions with large language models (LLMs).

- **LLMInterface.py** → Abstraction for LLM communication.
- **LLMProviderFactory.py** → Creates LLM provider based on config.
- **LLMEnums.py** → Available LLM choices (Cohere, Gemini, etc.).

#### **📁 llm/providers/**
Each provider implements its LLM logic:

- **CoHereProvider.py**
- **GeminiProvider.py**

#### **📁 llm/templates/**
Contains prompt templates and parsing logic.

- **Template_parser.py** → Replaces variables in templates.
- **locales/**
  - **ar/** → Arabic RAG templates  
    - `rag.py`
  - **en/** → English RAG templates  
    - `rag.py`

---

### **Other Root Files**

- **main.py** → FastAPI application entry point.
- **.env / .env.example** → Environment configuration.
- **requirements.txt** → Installed Python dependencies.

---
## 🚀 Requirements

- **Python 3.8+**
- (Optional) **MiniConda** for environment isolation
- (Optional) **Docker** for running vector DB or related services

---

## 📦 Environment Setup

You can set up your environment using either **MiniConda (recommended)** or Python's built-in **venv**.

---

### 🟢 Option 1 — Setup Using MiniConda (Recommended)

1. Install MiniConda from 👉 [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)

2. Create a new environment:

```bash
conda create -n rag-app python=3.8
```

3) Activate the environment:
```bash
$ conda activate rag-app
```
---
### 🟡 Option 2 — Setup Using Python venv
```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```
---
### (Optional) Improve Terminal Readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

### 📥 Install Dependencies

```bash
$ pip install -r requirements.txt
```
---
## 🔧 Environment Variables

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `GEMINI_API_KEY` value.

## 🐳 Run Docker Services (Vector DB, etc.)

```bash
$ cd docker
$ cp .env.example .env
```

- update `.env` with your credentials



```bash
$ cd docker
$ sudo docker compose up -d
```

## Run the fastapi server 

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection 

Dowenload the POSTMAN collection from [src/assets/rag-app.postman_collection.json](src/assets/rag-app.postman_collection.json)