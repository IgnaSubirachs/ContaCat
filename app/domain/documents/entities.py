from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Document:
    """Document entity for file attachments."""
    entity_type: str  # "PARTNER", "EMPLOYEE"
    entity_id: str  # ID of the related entity
    filename: str  # Original filename
    file_path: str  # Path where file is stored
    file_type: str  # MIME type
    document_type: str  # "DNI", "CONTRACT", "CERTIFICATE", "OTHER"
    file_size: int  # Size in bytes
    uploaded_by: str  # Who uploaded
    uploaded_at: datetime
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if isinstance(self.uploaded_at, str):
            self.uploaded_at = datetime.fromisoformat(self.uploaded_at)
    
    @property
    def file_size_mb(self) -> float:
        """Return file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_image(self) -> bool:
        """Check if document is an image."""
        return self.file_type.startswith("image/")
    
    @property
    def is_pdf(self) -> bool:
        """Check if document is a PDF."""
        return self.file_type == "application/pdf"
    
    def validate(self) -> None:
        """Validate document data."""
        if not self.filename or len(self.filename.strip()) == 0:
            raise ValueError("El nom del fitxer és obligatori")
        
        if not self.entity_type or not self.entity_id:
            raise ValueError("El tipus i ID de l'entitat són obligatoris")
        
        if self.file_size <= 0:
            raise ValueError("La mida del fitxer ha de ser superior a 0")
        
        # Max 10MB
        if self.file_size > 10 * 1024 * 1024:
            raise ValueError("El fitxer no pot superar els 10MB")
        
        # Allowed types
        allowed_types = [
            "image/jpeg", "image/png", "image/jpg",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if self.file_type not in allowed_types:
            raise ValueError(f"Tipus de fitxer no permès: {self.file_type}")
