from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
import json
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    APP_NAME: str = "rag_app"
    APP_VERSION: str = "0.1"

    FILE_ALLOWED_TYPES: List[str] = ["application/pdf", "text/plain"]
    FILE_MAX_SIZE: int = 10485760
    FILE_DEFAULT_CHUNK_SIZE: int = 512000

    # Supabase Config - read from env with fallback
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
    SUPABASE_BUCKET: str = "rag-files"
    
    # LLM Config - Generation uses OpenRouter, Embeddings use Gemini
    GENERATION_BACKEND: str = "OPENROUTER"
    EMBEDDING_BACKEND: str = "GEMINI"
    
    # OpenRouter Config (for text generation)
    OPENROUTER_API_KEY: Optional[str] = os.environ.get("OPENROUTER_API_KEY", None)
    
    # Gemini Config (for embeddings)
    GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY", None)
    COHERE_API_KEY: Optional[str] = os.environ.get("COHERE_API_KEY", None)
    
    GENERATION_MODEL_ID: Optional[str] = "qwen/qwen3-4b:free"
    EMBEDDING_MODEL_ID: Optional[str] = "text-embedding-004"
    EMBEDDING_MODEL_SIZE: Optional[int] = 768
    INPUT_DEFAULT_MAX_CHARACTERS: Optional[int] = 1024
    GENERATION_DEFAULT_MAX_TOKENS: Optional[int] = 500
    GENERATION_DEFAULT_TEMPERATURE: Optional[float] = 0.7

    # Qdrant Cloud Config
    VECTOR_DB_BACKEND: str = "QDRANT"
    QDRANT_URL: Optional[str] = os.environ.get("QDRANT_URL", None)
    QDRANT_API_KEY: Optional[str] = os.environ.get("QDRANT_API_KEY", None)
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = "cosine"

    PRIMARY_LANG: str = "ar"
    DEFAULT_LANG: str = "ar"
    
    @field_validator('FILE_ALLOWED_TYPES', mode='before')
    @classmethod
    def parse_file_types(cls, v):
        if isinstance(v, str):
            # Try to parse as JSON
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Split by comma if not valid JSON
                return [x.strip().strip('"\'') for x in v.strip('[]').split(',')]
        return v


def get_settings():
    return Settings()

