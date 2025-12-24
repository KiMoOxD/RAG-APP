from .BaseController import BaseController


class ProjectController(BaseController):
    """Controller for project-related operations"""
    
    def __init__(self):
        super().__init__()
    
    def get_project_storage_path(self, project_id: str) -> str:
        """
        Get the storage path prefix for a project in Supabase Storage
        
        Args:
            project_id: The project identifier
            
        Returns:
            Storage path prefix (e.g., 'project123/')
        """
        return f"{project_id}/"