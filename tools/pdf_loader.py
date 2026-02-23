from utils.flow_logger import function_logger
"""PDF handling tools."""

import os
import shutil
from typing import Tuple, Optional


class PDFProcessor:
    """Utilities for PDF extraction and chunking."""
    
    @staticmethod
    @function_logger("Execute extract text")
    def extract_text(file_path: str) -> str:
        """Extract all text from PDF (PHASE 3+)."""
        raise NotImplementedError("PHASE 3")
    
    @staticmethod
    @function_logger("Execute chunk pdf content")
    def chunk_pdf_content(text: str, chunk_size: int = 500) -> list:
        """Split PDF text into overlapping chunks (PHASE 3+)."""
        raise NotImplementedError("PHASE 3")
    
    @staticmethod
    @function_logger("Execute save uploaded pdf")
    def save_uploaded_pdf(uploaded_file, session_temp_dir: str) -> Tuple[str, dict]:
        """
        Save uploaded PDF to session temp directory (PHASE 1).
        
        Args:
            uploaded_file: Streamlit uploaded file object
            session_temp_dir: Session temp directory
            
        Returns:
            (file_path, metadata_dict)
        """
        # Create uploads subdirectory in session temp
        uploads_dir = os.path.join(session_temp_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(uploads_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Get file metadata
        file_size = os.path.getsize(file_path)
        metadata = {
            "filename": uploaded_file.name,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "path": file_path,
        }
        
        return file_path, metadata
    
    @staticmethod
    @function_logger("Delete file")
    def delete_file(file_path: str) -> bool:
        """
        Delete a file safely (PHASE 1).
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
