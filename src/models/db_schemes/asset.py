from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Asset(BaseModel):
    id: Optional[str] = Field(default=None)
    asset_project_id: str
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: Optional[dict] = Field(default=None)
    asset_pushed_at: Optional[datetime] = Field(default=None)
    asset_storage_path: Optional[str] = Field(default=None)  # Path in Supabase Storage

    model_config = {
        "arbitrary_types_allowed": True,
    }
    
    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = {
            "asset_project_id": self.asset_project_id,
            "asset_type": self.asset_type,
            "asset_name": self.asset_name,
            "asset_size": self.asset_size,
            "asset_storage_path": self.asset_storage_path,
        }
        if self.id:
            data["id"] = self.id
        if self.asset_config:
            data["asset_config"] = self.asset_config
        if self.asset_pushed_at:
            data["asset_pushed_at"] = self.asset_pushed_at.isoformat()
        else:
            data["asset_pushed_at"] = datetime.utcnow().isoformat()
        return data
    
    @classmethod
    def from_db_record(cls, record: dict) -> "Asset":
        """Create Asset from database record"""
        pushed_at = record.get("asset_pushed_at")
        if isinstance(pushed_at, str):
            pushed_at = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
        
        return cls(
            id=record.get("id"),
            asset_project_id=record.get("asset_project_id"),
            asset_type=record.get("asset_type"),
            asset_name=record.get("asset_name"),
            asset_size=record.get("asset_size"),
            asset_config=record.get("asset_config"),
            asset_pushed_at=pushed_at,
            asset_storage_path=record.get("asset_storage_path")
        )