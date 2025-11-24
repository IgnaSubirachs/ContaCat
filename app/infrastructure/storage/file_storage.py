"""
File storage service for handling document uploads.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple


class FileStorageService:
    """Service for storing and managing uploaded files."""
    
    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_file(
        self,
        file_content: bytes,
        filename: str,
        entity_type: str,
        entity_id: str
    ) -> Tuple[str, int]:
        """
        Save a file and return (file_path, file_size).
        
        Files are organized as: uploads/{entity_type}/{entity_id}/{timestamp}_{filename}
        """
        # Create directory structure
        entity_dir = self.base_path / entity_type.lower() / entity_id
        entity_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = self._sanitize_filename(filename)
        unique_filename = f"{timestamp}_{safe_filename}"
        
        # Full path
        file_path = entity_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Get file size
        file_size = len(file_content)
        
        # Return relative path from base
        relative_path = str(file_path.relative_to(self.base_path))
        
        return relative_path, file_size
    
    def delete_file(self, file_path: str) -> None:
        """Delete a file."""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
    
    def get_file_path(self, file_path: str) -> Path:
        """Get full path to a file."""
        return self.base_path / file_path
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return (self.base_path / file_path).exists()
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal."""
        # Remove any path components
        filename = os.path.basename(filename)
        # Remove potentially dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        return "".join(c if c in safe_chars else "_" for c in filename)
