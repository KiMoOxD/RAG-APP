from fastapi import APIRouter
from datetime import datetime 


health_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1", "health"],
)


@health_router.get("/health")
async def health_check():
    """
    Health check endpoint for DevOps monitoring.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }