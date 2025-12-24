from pydantic import BaseModel, Field
from typing import Optional
import json


class DataChunk(BaseModel):
    id: Optional[str] = Field(default=None)
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: str
    chunk_asset_id: str
    
    model_config = {
        "arbitrary_types_allowed": True,
    }
    
    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = {
            "chunk_text": self.chunk_text,
            "chunk_metadata": json.dumps(self.chunk_metadata) if isinstance(self.chunk_metadata, dict) else self.chunk_metadata,
            "chunk_order": self.chunk_order,
            "chunk_project_id": self.chunk_project_id,
            "chunk_asset_id": self.chunk_asset_id,
        }
        if self.id:
            data["id"] = self.id
        return data
    
    @classmethod
    def from_db_record(cls, record: dict) -> "DataChunk":
        """Create DataChunk from database record"""
        metadata = record.get("chunk_metadata", {})
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        return cls(
            id=record.get("id"),
            chunk_text=record.get("chunk_text"),
            chunk_metadata=metadata,
            chunk_order=record.get("chunk_order"),
            chunk_project_id=record.get("chunk_project_id"),
            chunk_asset_id=record.get("chunk_asset_id")
        )

        
class RetrievedDocument(BaseModel):
    text: str
    score: float