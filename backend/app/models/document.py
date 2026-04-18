"""
Document Models
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

from .base import BaseModel


class Document(BaseModel, table=True):
    """Document model"""
    __tablename__ = "documents"
    
    filename: str = Field(sa_column=Field(..., max_length=500))
    original_name: str = Field(sa_column=Field(..., max_length=500))
    file_path: str = Field(sa_column=Field(..., max_length=1000))
    file_size: Optional[int] = None
    file_type: Optional[str] = Field(default=None, max_length=50)
    status: str = Field(default="pending", max_length=50)  # pending, processing, completed, failed
    total_chunks: Optional[int] = None
    metadata_: Optional[dict] = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    
    # Relationships
    chunks: list["DocumentChunk"] = Relationship(back_populates="document")


class DocumentChunk(BaseModel, table=True):
    """Document chunk model"""
    __tablename__ = "document_chunks"
    
    document_id: int = Field(foreign_key="documents.id")
    chunk_index: int
    content: str
    embedding_id: Optional[str] = Field(default=None, max_length=100)
    page_number: Optional[int] = None
    coordinates: Optional[dict] = Field(default_factory=dict, sa_column=Column("coordinates", JSON))
    chunk_type: str = Field(default="text", max_length=50)  # text, table, image
    metadata_: Optional[dict] = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    
    # Relationships
    document: Optional[Document] = Relationship(back_populates="chunks")
    
    class Config:
        arbitrary_types_allowed = True


# Pydantic models for API
class DocumentUploadResponse(SQLModel):
    """Document upload response"""
    document_id: int
    filename: str
    status: str
    message: str


class DocumentStatusResponse(SQLModel):
    """Document status response"""
    document_id: int
    filename: str
    status: str
    progress: Optional[float] = None
    total_chunks: Optional[int] = None
    processed_chunks: Optional[int] = None


class ChunkResponse(SQLModel):
    """Document chunk response"""
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    chunk_type: str
    metadata: Optional[dict] = None


class DocumentListResponse(SQLModel):
    """Document list response"""
    documents: list[Document]
    total: int


class DocumentDeleteResponse(SQLModel):
    """Document delete response"""
    document_id: int
    message: str