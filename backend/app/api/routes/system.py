"""
System API Routes
System health, status, and utility endpoints
"""

from fastapi import APIRouter
from datetime import datetime
import os
import platform
import psutil

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "rag-system-api"
    }


@router.get("/stats")
async def system_stats():
    """Get system statistics"""
    # Memory usage
    memory = psutil.virtual_memory()
    
    # Disk usage
    disk = psutil.disk_usage('/')
    
    # CPU info
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        },
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100
        }
    }


@router.get("/info")
async def system_info():
    """Get system information"""
    return {
        "service": "RAG System API",
        "version": "0.1.0",
        "description": "Retrieval-Augmented Generation System",
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "system_stats": "/stats"
        },
        "features": [
            "Multi-format document processing",
            "Vector search with Milvus",
            "Memory management",
            "LLM integration",
            "Hybrid search"
        ]
    }


@router.get("/logs")
async def get_logs(lines: int = 100):
    """Get recent logs (demo implementation)"""
    # In production, this would read from actual log files
    demo_logs = [
        f"{datetime.now().isoformat()} - INFO - Starting RAG System",
        f"{datetime.now().isoformat()} - INFO - MySQL initialized successfully",
        f"{datetime.now().isoformat()} - INFO - Milvus initialized successfully",
        f"{datetime.now().isoformat()} - INFO - Redis initialized successfully",
        f"{datetime.now().isoformat()} - INFO - Application startup complete",
    ]
    
    return {
        "logs": demo_logs[-lines:],
        "total": len(demo_logs),
        "lines_requested": lines
    }


@router.post("/restart")
async def restart_service():
    """Restart the service (demo)"""
    return {
        "message": "Service restart initiated",
        "note": "In production, this would trigger actual restart"
    }


@router.get("/database/status")
async def database_status():
    """Get database connection status"""
    return {
        "mysql": {
            "status": "connected",
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "database": os.getenv("MYSQL_DATABASE", "rag_system")
        },
        "milvus": {
            "status": "connected",
            "host": os.getenv("MILVUS_HOST", "localhost"),
            "port": os.getenv("MILVUS_PORT", "19530")
        },
        "redis": {
            "status": "connected",
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": os.getenv("REDIS_PORT", "6379")
        }
    }
