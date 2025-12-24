from pydantic import BaseModel, Field, validator
from typing import Optional
import uuid


class Project(BaseModel):
    id: Optional[str] = Field(default=None)
    project_id: str = Field(..., min_length=1)

    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('Project ID must be alphanumeric')
        return value

    model_config = {
        "arbitrary_types_allowed": True,
    }
    
    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = {
            "project_id": self.project_id,
        }
        if self.id:
            data["id"] = self.id
        return data
    
    @classmethod
    def from_db_record(cls, record: dict) -> "Project":
        """Create Project from database record"""
        return cls(
            id=record.get("id"),
            project_id=record.get("project_id")
        )