from supabase import create_client, Client
from helpers.config import Settings
import logging

logger = logging.getLogger(__name__)


class SupabaseProvider:
    """Supabase client provider for database and storage operations"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Client = None
        self.storage_bucket = settings.SUPABASE_BUCKET
        
    def connect(self) -> Client:
        """Initialize and return Supabase client"""
        try:
            self.client = create_client(
                self.settings.SUPABASE_URL,
                self.settings.SUPABASE_KEY
            )
            logger.info("Successfully connected to Supabase")
            return self.client
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def disconnect(self):
        """Cleanup Supabase connection"""
        self.client = None
        logger.info("Disconnected from Supabase")
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        if not self.client:
            self.connect()
        return self.client
    
    # ==================== Database Operations ====================
    
    def table(self, table_name: str):
        """Get a table reference for database operations"""
        return self.client.table(table_name)
    
    # ==================== Storage Operations ====================
    
    async def ensure_bucket_exists(self):
        """Ensure the storage bucket exists, create if not"""
        try:
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if self.storage_bucket not in bucket_names:
                self.client.storage.create_bucket(
                    self.storage_bucket,
                    options={"public": False}
                )
                logger.info(f"Created storage bucket: {self.storage_bucket}")
            return True
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            return False
    
    def upload_file(self, file_path: str, file_content: bytes, content_type: str = None) -> dict:
        """
        Upload a file to Supabase Storage
        
        Args:
            file_path: Path in the bucket (e.g., 'project_id/filename.pdf')
            file_content: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            dict with upload result
        """
        try:
            options = {}
            if content_type:
                options["content-type"] = content_type
                
            result = self.client.storage.from_(self.storage_bucket).upload(
                path=file_path,
                file=file_content,
                file_options=options
            )
            logger.info(f"Successfully uploaded file: {file_path}")
            return {"success": True, "path": file_path, "result": result}
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def download_file(self, file_path: str) -> bytes:
        """
        Download a file from Supabase Storage
        
        Args:
            file_path: Path in the bucket
            
        Returns:
            File content as bytes
        """
        try:
            response = self.client.storage.from_(self.storage_bucket).download(file_path)
            return response
        except Exception as e:
            logger.error(f"Failed to download file {file_path}: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage
        
        Args:
            file_path: Path in the bucket
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.storage.from_(self.storage_bucket).remove([file_path])
            logger.info(f"Successfully deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Get a signed URL for a file
        
        Args:
            file_path: Path in the bucket
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Signed URL string
        """
        try:
            response = self.client.storage.from_(self.storage_bucket).create_signed_url(
                file_path, expires_in
            )
            return response.get("signedURL")
        except Exception as e:
            logger.error(f"Failed to get signed URL for {file_path}: {e}")
            return None
    
    def list_files(self, folder_path: str = "") -> list:
        """
        List files in a folder
        
        Args:
            folder_path: Folder path in the bucket
            
        Returns:
            List of file objects
        """
        try:
            files = self.client.storage.from_(self.storage_bucket).list(folder_path)
            return files
        except Exception as e:
            logger.error(f"Failed to list files in {folder_path}: {e}")
            return []
