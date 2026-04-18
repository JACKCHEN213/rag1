"""
Redis Connection Management
"""

import json
from typing import Optional, List, Dict, Any
import redis

from app.config import settings

_redis_client = None


async def init_redis():
    """Initialize Redis connection"""
    global _redis_client
    
    try:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            encoding="utf-8",
        )
        
        # Test connection
        _redis_client.ping()
        
        print("✓ Redis initialized successfully")
        
    except Exception as e:
        print(f"✗ Redis initialization failed: {e}")
        raise


def get_redis():
    """Get Redis client"""
    global _redis_client
    
    if _redis_client is None:
        raise RuntimeError("Redis not initialized")
    
    return _redis_client


# Short-term memory functions
def save_conversation(session_id: str, messages: List[Dict[str, Any]]) -> bool:
    """Save conversation messages to Redis"""
    redis_client = get_redis()
    key = f"conversation:{session_id}"
    
    try:
        # Save conversation with TTL (7 days)
        redis_client.setex(key, 7 * 24 * 60 * 60, json.dumps(messages))
        return True
    except Exception:
        return False


def get_conversation(session_id: str) -> Optional[List[Dict[str, Any]]]:
    """Get conversation messages from Redis"""
    redis_client = get_redis()
    key = f"conversation:{session_id}"
    
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


def add_conversation_message(session_id: str, message: Dict[str, Any]) -> bool:
    """Add a message to conversation"""
    messages = get_conversation(session_id) or []
    messages.append(message)
    
    # Keep only recent messages
    max_size = settings.SHORT_MEMORY_SIZE
    if len(messages) > max_size:
        messages = messages[-max_size:]
    
    return save_conversation(session_id, messages)


def clear_conversation(session_id: str) -> bool:
    """Clear conversation"""
    redis_client = get_redis()
    key = f"conversation:{session_id}"
    
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False


# Cache functions
def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """Set cache value"""
    redis_client = get_redis()
    
    try:
        redis_client.setex(key, expire, json.dumps(value))
        return True
    except Exception:
        return False


def get_cache(key: str) -> Optional[Any]:
    """Get cache value"""
    redis_client = get_redis()
    
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


def delete_cache(key: str) -> bool:
    """Delete cache value"""
    redis_client = get_redis()
    
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False


def delete_cache_pattern(pattern: str) -> bool:
    """Delete cache values matching pattern"""
    redis_client = get_redis()
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception:
        return False


# Task status tracking (for async operations)
def set_task_status(task_id: str, status: str, result: Optional[Dict] = None) -> bool:
    """Set task status"""
    redis_client = get_redis()
    key = f"task:{task_id}"
    
    data = {
        "status": status,  # pending, processing, completed, failed
        "result": result,
    }
    
    try:
        # Keep task status for 24 hours
        redis_client.setex(key, 24 * 60 * 60, json.dumps(data))
        return True
    except Exception:
        return False


def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task status"""
    redis_client = get_redis()
    key = f"task:{task_id}"
    
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


# Rate limiting
def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """Check rate limit"""
    redis_client = get_redis()
    
    try:
        current = redis_client.get(key)
        if current is None:
            redis_client.setex(key, window, 0)
            current = 0
        
        if int(current) >= limit:
            return False
        
        redis_client.incr(key)
        return True
    except Exception:
        return False


def check_redis_connection() -> bool:
    """Check if Redis connection is alive"""
    global _redis_client
    
    if _redis_client is None:
        return False
    
    try:
        _redis_client.ping()
        return True
    except Exception:
        return False