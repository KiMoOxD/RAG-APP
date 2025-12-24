from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
import logging

logger = logging.getLogger(__name__)


class ChunkModel(BaseDataModel):
    """Chunk model using Supabase PostgreSQL"""

    def __init__(self, supabase_client):
        super().__init__(supabase_client=supabase_client)
        self.table_name = "chunks"
        
    @classmethod
    async def create_instance(cls, db_client):
        """Factory method to create ChunkModel instance"""
        instance = cls(db_client)
        return instance
            
    async def create_chunk(self, chunk: DataChunk) -> DataChunk:
        """Create a new chunk in the database"""
        try:
            result = self.table().insert(chunk.to_db_dict()).execute()
            
            if result.data and len(result.data) > 0:
                chunk.id = result.data[0].get("id")
                return chunk
            return None
        except Exception as e:
            logger.error(f"Error creating chunk: {e}")
            raise

    async def get_chunk(self, chunk_id: str):
        """Get a chunk by ID"""
        try:
            result = self.table().select("*").eq("id", chunk_id).execute()
            
            if result.data and len(result.data) > 0:
                return DataChunk.from_db_record(result.data[0])
            
            return None
        except Exception as e:
            logger.error(f"Error getting chunk: {e}")
            raise

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100) -> int:
        """Insert multiple chunks in batches"""
        try:
            total_inserted = 0
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                batch_data = [chunk.to_db_dict() for chunk in batch]
                
                result = self.table().insert(batch_data).execute()
                total_inserted += len(result.data) if result.data else 0
            
            return total_inserted
        except Exception as e:
            logger.error(f"Error inserting many chunks: {e}")
            raise

    async def delete_chunks_by_project_id(self, project_id: str) -> int:
        """Delete all chunks for a project"""
        try:
            # First count how many will be deleted
            count_result = self.table().select("id", count="exact").eq(
                "chunk_project_id", project_id
            ).execute()
            deleted_count = count_result.count or 0
            
            # Delete the chunks
            self.table().delete().eq("chunk_project_id", project_id).execute()
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting chunks by project ID: {e}")
            raise
    
    async def get_poject_chunks(self, project_id: str, page_no: int = 1, page_size: int = 50):
        """Get chunks for a project with pagination"""
        try:
            offset = (page_no - 1) * page_size
            
            result = self.table().select("*").eq(
                "chunk_project_id", project_id
            ).order(
                "chunk_order"
            ).range(
                offset, offset + page_size - 1
            ).execute()
            
            return [
                DataChunk.from_db_record(record)
                for record in result.data
            ]
        except Exception as e:
            logger.error(f"Error getting project chunks: {e}")
            raise