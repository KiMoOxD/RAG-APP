from .BaseDataModel import BaseDataModel
from .db_schemes import Project
import logging

logger = logging.getLogger(__name__)


class ProjectModel(BaseDataModel):
    """Project model using Supabase PostgreSQL"""

    def __init__(self, supabase_client):
        super().__init__(supabase_client=supabase_client)
        self.table_name = "projects"
        
    @classmethod
    async def create_instance(cls, db_client):
        """Factory method to create ProjectModel instance"""
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project) -> Project:
        """Create a new project in the database"""
        try:
            result = self.table().insert(project.to_db_dict()).execute()
            
            if result.data and len(result.data) > 0:
                project.id = result.data[0].get("id")
                return project
            return None
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise

    async def get_project_or_create(self, project_id: str) -> Project:
        """Get existing project or create new one"""
        try:
            # Try to find existing project
            result = self.table().select("*").eq("project_id", project_id).execute()
            
            if result.data and len(result.data) > 0:
                return Project.from_db_record(result.data[0])
            
            # Create new project if not found
            project = Project(project_id=project_id)
            return await self.create_project(project=project)
        except Exception as e:
            logger.error(f"Error in get_project_or_create: {e}")
            raise

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        """Get all projects with pagination"""
        try:
            # Get total count
            count_result = self.table().select("*", count="exact").execute()
            total_documents = count_result.count or 0
            
            # Calculate total pages
            total_pages = total_documents // page_size
            if total_documents % page_size > 0:
                total_pages += 1
            
            # Get paginated results
            offset = (page - 1) * page_size
            result = self.table().select("*").range(offset, offset + page_size - 1).execute()
            
            projects = [
                Project.from_db_record(record)
                for record in result.data
            ]
            
            return projects, total_pages
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            raise
