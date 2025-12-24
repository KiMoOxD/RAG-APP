from .BaseController import BaseController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum
import tempfile
import os


class ProcessController(BaseController):
    """Controller for file processing operations"""
    
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id

    def get_file_extension(self, file_id: str):
        """Get file extension from file ID"""
        return os.path.splitext(file_id)[-1]

    def get_file_loader_from_bytes(self, file_content: bytes, file_id: str):
        """
        Get appropriate file loader based on file extension
        Creates a temporary file from bytes for processing
        
        Args:
            file_content: File content as bytes
            file_id: File identifier
            
        Returns:
            Document loader or None
        """
        file_ext = self.get_file_extension(file_id=file_id)
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            if file_ext == ProcessingEnum.TXT.value:
                return TextLoader(temp_path, encoding="utf-8"), temp_path
            elif file_ext == ProcessingEnum.PDF.value:
                return PyMuPDFLoader(temp_path), temp_path
            else:
                os.unlink(temp_path)  # Clean up temp file
                return None, None
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None, None

    def get_file_content_from_bytes(self, file_bytes: bytes, file_id: str):
        """
        Load file content from bytes
        
        Args:
            file_bytes: File content as bytes
            file_id: File identifier
            
        Returns:
            Loaded document content or None
        """
        loader, temp_path = self.get_file_loader_from_bytes(file_bytes, file_id)
        
        if loader is None:
            return None
        
        try:
            content = loader.load()
            return content
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        
    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int = 100, overlap_size: int = 20):
        """
        Process file content into chunks
        
        Args:
            file_content: List of document objects
            file_id: File identifier
            chunk_size: Size of each chunk
            overlap_size: Overlap between chunks
            
        Returns:
            List of document chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        file_content_text = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(
            file_content_text, 
            metadatas=file_content_metadata
        )

        return chunks