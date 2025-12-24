from .ProjectController import ProjectController
from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import re


class DataController(BaseController):
    """Controller for data/file operations"""
    
    def __init__(self):
        super().__init__()
    
    def validate_file_properties(self, file: UploadFile):
        """
        Validate file properties (type and size)
        
        Args:
            file: Uploaded file
            
        Returns:
            Tuple of (is_valid, result_signal)
        """
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value
    
    def generate_unique_file_id(self, orig_file_name: str, project_id: str):
        """
        Generate a unique file ID and storage path for Supabase Storage
        
        Args:
            orig_file_name: Original file name
            project_id: Project ID
            
        Returns:
            Tuple of (storage_path, file_id)
        """
        random_key = self.generate_random_string()
        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)
        
        file_id = f"{random_key}_{cleaned_file_name}"
        storage_path = f"{project_id}/{file_id}"
        
        return storage_path, file_id

    def get_clean_file_name(self, orig_file_name: str):
        """
        Clean file name by removing special characters
        
        Args:
            orig_file_name: Original file name
            
        Returns:
            Cleaned file name
        """
        # Remove any special characters except for dot and underscore
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
        # Replace spaces with underscores
        cleaned_file_name = cleaned_file_name.replace(" ", "_")
        return cleaned_file_name
