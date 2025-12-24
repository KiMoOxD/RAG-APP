from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums


class VectorDBProviderFactory:
    """Factory for creating vector database providers"""
    
    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        """
        Create a vector database provider
        
        Args:
            provider: Provider type (e.g., 'QDRANT')
            
        Returns:
            Vector database provider instance
        """
        if provider == VectorDBEnums.QDRANT.value:
            # Check if cloud credentials are provided
            qdrant_url = getattr(self.config, 'QDRANT_URL', None)
            qdrant_api_key = getattr(self.config, 'QDRANT_API_KEY', None)
            
            if qdrant_url and qdrant_api_key:
                # Use Qdrant Cloud
                return QdrantDBProvider(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                )
            else:
                # Fall back to local Qdrant (not recommended)
                db_path = getattr(self.config, 'VECTOR_DB_PATH', 'qdrant_db')
                return QdrantDBProvider(
                    db_path=db_path,
                    distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                )
        
        return None