"""
Memory Models
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from enum import Enum

from .base import BaseModel


class MemoryType(str, Enum):
    """Memory type enum"""
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    PREFERENCE = "preference"
    ENTITY = "entity"
    TASK = "task"


class LongTermMemory(BaseModel, table=True):
    """Long term memory model"""
    __tablename__ = "long_term_memory"
    
    memory_type: str = Field(max_length=50)
    content: str
    embedding_id: Optional[str] = Field(default=None, max_length=100)
    importance_score: Optional[float] = None
    last_accessed: Optional[datetime] = None
    access_count: int = Field(default=0)
    metadata_: Optional[dict] = Field(default_factory=dict, sa_column=Column("metadata", JSON))


class Conversation(BaseModel, table=True):
    """Conversation history model"""
    __tablename__ = "conversations"
    
    session_id: str = Field(max_length=100, index=True)
    user_message: str
    assistant_message: str
    retrieved_chunks: Optional[list] = Field(default_factory=list, sa_column=Column("retrieved_chunks", JSON))
    metadata_: Optional[dict] = Field(default_factory=dict, sa_column=Column("metadata", JSON))


# Pydantic models for API
class ShortMemoryResponse(SQLModel):
    """Short term memory response"""
    session_id: str
    messages: List[dict]
    size: int


class LongMemoryCreate(SQLModel):
    """Long term memory create request"""
    memory_type: MemoryType
    content: str
    importance_score: Optional[float] = None
    metadata: Optional[dict] = None


class LongMemoryResponse(SQLModel):
    """Long term memory response"""
    memory_id: int
    memory_type: MemoryType
    content: str
    importance_score: Optional[float]
    last_accessed: Optional[datetime]
    access_count: int
    created_at: datetime
    metadata: Optional[dict]


class MemoryListResponse(SQLModel):
    """Memory list response"""
    memories: List[LongMemoryResponse]
    total: int


class MemoryImportanceUpdate(SQLModel):
    """Memory importance update request"""
    importance_score: float