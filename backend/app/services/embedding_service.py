"""
Embedding Service
Generates embeddings for text chunks using BGE-M3 model
"""

from typing import List, Tuple, Dict, Any
import numpy as np
import uuid
from sentence_transformers import SentenceTransformer

from app.config import settings

# Global model instance
_embedding_model = None


def get_embedding_model():
    """Get or create embedding model instance"""
    global _embedding_model
    
    if _embedding_model is None:
        device = settings.EMBEDDING_DEVICE
        if device == "auto":
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        _embedding_model = SentenceTransformer(
            settings.EMBEDDING_MODEL_NAME,
            device=device
        )
    
    return _embedding_model


async def generate_embeddings_batch(texts: List[str]) -> Tuple[List[List[float]], List[Dict[int, float]]]:
    """
    Generate embeddings for a batch of texts
    
    Returns:
        Tuple of (dense_embeddings, sparse_embeddings)
    """
    model = get_embedding_model()
    
    # Generate dense embeddings
    dense_embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    ).tolist()
    
    # Generate sparse embeddings (placeholder - using simple token-based approach)
    sparse_embeddings = []
    for text in texts:
        # Simple token frequency as sparse embedding
        tokens = text.lower().split()
        token_freq = {}
        for i, token in enumerate(set(tokens)):
            token_freq[i] = tokens.count(token)
        sparse_embeddings.append(token_freq)
    
    return dense_embeddings, sparse_embeddings


async def generate_query_embedding(query: str) -> Tuple[List[float], Dict[int, float]]:
    """Generate embedding for a query"""
    dense_embeddings, sparse_embeddings = await generate_embeddings_batch([query])
    return dense_embeddings[0], sparse_embeddings[0]


async def generate_document_embedding(text: str) -> Tuple[List[float], Dict[int, float]]:
    """Generate embedding for a document chunk"""
    return await generate_query_embedding(text)


# Reranker service placeholder
async def rerank_results(query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
    """
    Rerank documents based on query relevance
    
    Returns:
        List of (doc_index, score) tuples
    """
    # Placeholder implementation - using simple keyword matching
    # In production, use BGE-Reranker model
    
    scores = []
    query_tokens = set(query.lower().split())
    
    for idx, doc in enumerate(documents):
        doc_tokens = set(doc.lower().split())
        overlap = len(query_tokens & doc_tokens)
        score = overlap / len(query_tokens) if query_tokens else 0
        scores.append((idx, score))
    
    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return scores[:top_k]
