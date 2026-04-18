"""
Configuration API Routes
Manages system configuration and settings
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ConfigUpdateRequest(BaseModel):
    """Configuration update request"""
    config_key: str
    config_value: Dict[str, Any]
    description: str = None


class ConfigResponse(BaseModel):
    """Configuration response"""
    config_key: str
    config_value: Dict[str, Any]
    description: str = None


# In-memory config store (replace with database in production)
_config_store = {
    "llm": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "embedding": {
        "model": "BAAI/bge-m3",
        "device": "auto"
    },
    "processing": {
        "chunk_size": 512,
        "chunk_overlap": 50
    }
}


@router.get("/")
async def get_all_config():
    """Get all configuration"""
    return {"config": _config_store}


@router.get("/{config_key}")
async def get_config(config_key: str):
    """Get specific configuration"""
    if config_key not in _config_store:
        raise HTTPException(status_code=404, detail=f"Config key '{config_key}' not found")
    
    return {
        "config_key": config_key,
        "config_value": _config_store[config_key]
    }


@router.put("/{config_key}")
async def update_config(config_key: str, request: ConfigUpdateRequest):
    """Update configuration"""
    _config_store[config_key] = request.config_value
    
    return {
        "message": f"Configuration '{config_key}' updated successfully",
        "config": _config_store[config_key]
    }


@router.get("/llm/providers")
async def get_llm_providers():
    """Get available LLM providers"""
    return {
        "providers": [
            {"name": "openai", "models": ["gpt-3.5-turbo", "gpt-4"]},
            {"name": "claude", "models": ["claude-3-haiku", "claude-3-sonnet"]},
            {"name": "local", "models": ["llama2", "mistral"]}
        ]
    }


@router.get("/prompts")
async def get_prompts():
    """Get system prompts"""
    return {
        "prompts": {
            "system": "You are a helpful AI assistant based on uploaded documents.",
            "rag": "Use the following context to answer the question: {context}"
        }
    }


@router.put("/prompts")
async def update_prompts(prompt_type: str, content: str):
    """Update system prompts"""
    return {
        "message": f"Prompt '{prompt_type}' updated",
        "prompt": content
    }
