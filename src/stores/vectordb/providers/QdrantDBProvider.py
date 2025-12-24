from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):
    """Qdrant provider supporting both local and cloud connections"""

    def __init__(self, db_path: str = None, distance_method: str = None,
                 url: str = None, api_key: str = None):
        """
        Initialize Qdrant provider
        
        Args:
            db_path: Local path for Qdrant (deprecated, use url/api_key for cloud)
            distance_method: Distance method ('cosine' or 'dot')
            url: Qdrant Cloud URL
            api_key: Qdrant Cloud API key
        """
        self.client = None
        self.db_path = db_path
        self.url = url
        self.api_key = api_key
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        else:
            self.distance_method = models.Distance.COSINE  # Default

        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Connect to Qdrant (cloud or local)"""
        try:
            if self.url and self.api_key:
                # Connect to Qdrant Cloud
                self.client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key
                )
                self.logger.info(f"Connected to Qdrant Cloud: {self.url}")
            elif self.db_path:
                # Connect to local Qdrant
                self.client = QdrantClient(path=self.db_path)
                self.logger.info(f"Connected to local Qdrant: {self.db_path}")
            else:
                # In-memory Qdrant for testing
                self.client = QdrantClient(":memory:")
                self.logger.info("Connected to in-memory Qdrant")
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def disconnect(self):
        """Disconnect from Qdrant"""
        self.client = None
        self.logger.info("Disconnected from Qdrant")

    def is_collection_existed(self, collection_name: str) -> bool:
        """Check if collection exists"""
        try:
            return self.client.collection_exists(collection_name=collection_name)
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {e}")
            return False
    
    def list_all_collections(self) -> List:
        """List all collections"""
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        """Get collection information"""
        try:
            return self.client.get_collection(collection_name=collection_name)
        except Exception as e:
            self.logger.error(f"Error getting collection info: {e}")
            return None
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        """Create a collection"""
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            self.logger.info(f"Created collection: {collection_name}")
            return True
        
        return False
    
    def insert_one(self, collection_name: str, text: str, vector: list,
                        metadata: dict = None, 
                        record_id: str = None):
        """Insert a single record"""
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Cannot insert to non-existent collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id if isinstance(record_id, int) else hash(record_id) % (2**63),
                        vector=vector,
                        payload={
                            "text": text, 
                            "metadata": metadata
                        }
                    )
                ]
            )
            return True
        except Exception as e:
            self.logger.error(f"Error inserting record: {e}")
            return False
    
    def insert_many(self, collection_name: str, texts: list, 
                        vectors: list, metadata: list = None, 
                        record_ids: list = None, batch_size: int = 50):
        """Insert multiple records in batches"""
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_points = [
                models.PointStruct(
                    id=batch_record_ids[x] if isinstance(batch_record_ids[x], int) else hash(str(batch_record_ids[x])) % (2**63),
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x], 
                        "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            try:
                _ = self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points,
                )
            except Exception as e:
                self.logger.error(f"Error inserting batch: {e}")
                return False

        return True
        
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        """Search by vector similarity"""
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )

            if not results or len(results) == 0:
                return None
            
            return [
                RetrievedDocument(**{
                    "score": result.score,
                    "text": result.payload["text"],
                })
                for result in results
            ]
        except Exception as e:
            self.logger.error(f"Error searching: {e}")
            return None