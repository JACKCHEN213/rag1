"""
Chat API Routes
Handles conversation and message management
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


# Pydantic models
class Message(BaseModel):
    """Chat message model"""
    role: str  # user, assistant, system
    content: str
    
    
class ChatRequest(BaseModel):
    """Chat request"""
    messages: List[Message]
    stream: bool = True
    model: str = None
    temperature: float = 0.7
    max_tokens: int = 2000


class ChatResponse(BaseModel):
    """Chat response"""
    message: Message
    retrieved_chunks: List[dict] = None
    metadata: dict = {}


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    session_id: str
    messages: List[Message]
    total: int


# In-memory storage for demo (replace with Redis in production)
chat_sessions = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest, session_id: str = None):
    """
    Send a message and get response
    
    - If session_id provided, continues existing conversation
    - If no session_id, creates new conversation
    """
    # Demo implementation - replace with actual LLM integration
    import uuid
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get last user message
    user_messages = [msg for msg in chat_request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")
    
    user_message = user_messages[-1]
    
    # Demo response (replace with actual RAG logic)
    response_content = f"Demo response to: {user_message.content[:50]}..."
    
    # Store in session (simplified)
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # Add user message
    chat_sessions[session_id].extend(chat_request.messages)
    
    # Add assistant response
    assistant_msg = Message(role="assistant", content=response_content)
    chat_sessions[session_id].append(assistant_msg)
    
    return ChatResponse(
        message=assistant_msg,
        retrieved_chunks=[
            {"content": "Demo chunk 1", "score": 0.95},
            {"content": "Demo chunk 2", "score": 0.87}
        ],
        metadata={"session_id": session_id, "model": "demo"}
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = chat_sessions[session_id]
    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages,
        total=len(messages)
    )


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return {"message": "Chat history cleared", "session_id": session_id}


@router.get("/sessions")
async def get_active_sessions():
    """Get list of active chat sessions"""
    return {
        "sessions": list(chat_sessions.keys()),
        "total": len(chat_sessions)
    }


@router.post("/test-retrieval")
async def test_retrieval(query: str, top_k: int = 10):
    """Test document retrieval for a query"""
    # Demo retrieval - replace with actual vector search
    demo_chunks = [
        {"content": f"Demo chunk about {query}", "score": 0.95},
        {"content": "Another relevant chunk", "score": 0.87},
        {"content": "Less relevant chunk", "score": 0.72}
    ]
    
    return {
        "query": query,
        "top_k": top_k,
        "chunks": demo_chunks[:top_k]
    }
