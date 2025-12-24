from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base, data, nlp, health
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from stores.supabase.SupabaseProvider import SupabaseProvider
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    settings = get_settings()
    
    # Initialize Supabase client
    supabase_provider = SupabaseProvider(settings)
    supabase_provider.connect()
    app.supabase_provider = supabase_provider
    app.db_client = supabase_provider.get_client()
    
    # Ensure storage bucket exists
    await supabase_provider.ensure_bucket_exists()
    
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)
    
    # Generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )

    # Vector DB client 
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )
    
    logger.info("Application started successfully")
    logger.info(f"Connected to Supabase: {settings.SUPABASE_URL}")
    logger.info(f"Connected to Qdrant Cloud: {settings.QDRANT_URL}")
    
    yield
    
    # Shutdown
    app.supabase_provider.disconnect()
    app.vectordb_client.disconnect()
    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(health.health_router)
