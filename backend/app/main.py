"""
RAG System FastAPI Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.config import settings
from app.database.mysql import init_mysql
from app.database.milvus import init_milvus
from app.database.redis import init_redis
from app.api.routes import document, chat, config, memory, search, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting RAG System...")
    
    # Initialize databases
    await init_mysql()
    await init_milvus()
    await init_redis()
    
    print("RAG System started successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down RAG System...")


# Create FastAPI application
app = FastAPI(
    title="RAG System API",
    description="Document Retrieval Augmented Generation System",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(system.router, prefix="/api/system", tags=["system"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RAG System API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
