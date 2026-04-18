"""
Memory API Routes
Manages short-term and long-term memory
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class ShortMemoryRequest(BaseModel):
    """Short term memory request"""
    session_id: str
    messages: List[dict]


class LongMemoryCreate(BaseModel):
    """Long term memory create request"""
    memory_type: str
    content: str
    importance_score: Optional[float] = None


class MemoryResponse(BaseModel):
    """Memory response"""
    id: str
    memory_type: str
    content: str
    created_at: datetime


# Demo storage
_short_term_memory = {}
_long_term_memory = {}


@router.get("/short/{session_id}")
async def get_short_term_memory(session_id: str):
    """Get short term memory for session"""
    messages = _short_term_memory.get(session_id, [])
    return {
        "session_id": session_id,
        "messages": messages,
        "count": len(messages)
    }


@router.put("/short/{session_id}")
async def update_short_term_memory(session_id: str, request: ShortMemoryRequest):
    """Update short term memory"""
    _short_term_memory[session_id] = request.messages
    
    return {
        "message": "Short term memory updated",
        "session_id": session_id,
        "count": len(request.messages)
    }


@router.delete("/short/{session_id}")
async def clear_short_term_memory(session_id: str):
    """Clear short term memory"""
    if session_id in _short_term_memory:
        del _short_term_memory[session_id]
    
    return {"message": "Short term memory cleared", "session_id": session_id}


@router.get("/long")
async def get_long_term_memory(limit: int = 100, offset: int = 0):
    """Get long term memory entries"""
    memories = list(_long_term_memory.values())
    return {
        "memories": memories[offset:offset + limit],
        "total": len(memories),
        "limit": limit,
        "offset": offset
    }


@router.post("/long")
async def create_long_term_memory(memory: LongMemoryCreate):
    """Create long term memory entry"""
    memory_id = str(len(_long_term_memory) + 1)
    
    _long_term_memory[memory_id] = {
        "id": memory_id,
        "memory_type": memory.memory_type,
        "content": memory.content,
        "importance_score": memory.importance_score,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": "Long term memory created",
        "memory_id": memory_id
    }


@router.get("/long/search")
async def search_long_term_memory(query: str, limit: int = 10):
    """Search long term memory"""
    # Demo search
    results = []
    for memory_id, memory in _long_term_memory.items():
        if query.lower() in memory["content"].lower():
            results.append(memory)
    
    return {
        "query": query,
        "results": results[:limit],
        "total": len(results)
    }


@router.delete("/long/{memory_id}")
async def delete_long_term_memory(memory_id: str):
    """Delete long term memory entry"""
    if memory_id in _long_term_memory:
        del _long_term_memory[memory_id]
        return {"message": "Memory deleted", "memory_id": memory_id}
    else:
        raise HTTPException(status_code=404, detail="Memory not found")
