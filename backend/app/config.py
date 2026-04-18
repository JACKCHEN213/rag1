"""
Configuration Management
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "RAG System"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    SECRET_KEY: str = Field(default=secrets.token_urlsafe(32), env="SECRET_KEY")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database - MySQL
    MYSQL_HOST: str = Field(default="localhost", env="MYSQL_HOST")
    MYSQL_PORT: int = Field(default=3306, env="MYSQL_PORT")
    MYSQL_USER: str = Field(default="root", env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(default="", env="MYSQL_PASSWORD")
    MYSQL_DATABASE: str = Field(default="rag_system", env="MYSQL_DATABASE")
    
    @property
    def MYSQL_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # Database - Milvus
    MILVUS_HOST: str = Field(default="localhost", env="MILVUS_HOST")
    MILVUS_PORT: int = Field(default=19530, env="MILVUS_PORT")
    MILVUS_USER: Optional[str] = Field(default=None, env="MILVUS_USER")
    MILVUS_PASSWORD: Optional[str] = Field(default=None, env="MILVUS_PASSWORD")
    
    # Database - Redis
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Embedding Model
    EMBEDDING_MODEL_NAME: str = Field(default="BAAI/bge-m3", env="EMBEDDING_MODEL_NAME")
    EMBEDDING_DEVICE: str = Field(default="auto", env="EMBEDDING_DEVICE")  # auto, cpu, cuda
    EMBEDDING_BATCH_SIZE: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    
    # Reranker Model
    RERANKER_MODEL_NAME: str = Field(default="BAAI/bge-reranker-large", env="RERANKER_MODEL_NAME")
    RERANKER_DEVICE: str = Field(default="auto", env="RERANKER_DEVICE")
    RERANKER_TOP_K: int = Field(default=5, env="RERANKER_TOP_K")
    
    # LLM Configuration
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")  # openai, claude, local
    LLM_API_URL: str = Field(default="https://api.openai.com/v1", env="LLM_API_URL")
    LLM_API_KEY: Optional[str] = Field(default=None, env="LLM_API_KEY")
    LLM_MODEL_NAME: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL_NAME")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # File Upload
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".md", ".txt", ".jpg", ".png"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # Processing
    CHUNK_SIZE: int = Field(default=512, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=50, env="CHUNK_OVERLAP")
    MAX_WORKERS: int = Field(default=4, env="MAX_WORKERS")
    
    # Search
    DEFAULT_TOP_K: int = Field(default=10, env="DEFAULT_TOP_K")
    SEARCH_DISTANCE_THRESHOLD: float = Field(default=0.7, env="SEARCH_DISTANCE_THRESHOLD")
    
    # Memory
    SHORT_MEMORY_SIZE: int = Field(default=10, env="SHORT_MEMORY_SIZE")  # 保存最近10轮对话
    LONG_MEMORY_IMPORTANCE_THRESHOLD: float = Field(default=0.8, env="LONG_MEMORY_IMPORTANCE_THRESHOLD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
