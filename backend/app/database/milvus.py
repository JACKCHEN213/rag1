"""
Milvus Vector Database Connection Management
"""

from typing import Optional, List, Dict, Any
import numpy as np
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)

from app.config import settings

_milvus_client = None


async def init_milvus():
    """Initialize Milvus connection"""
    global _milvus_client
    
    try:
        # Connect to Milvus
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            user=settings.MILVUS_USER,
            password=settings.MILVUS_PASSWORD,
        )
        
        # Create collections if not exist
        _create_collections()
        
        print("✓ Milvus initialized successfully")
        
    except Exception as e:
        print(f"✗ Milvus initialization failed: {e}")
        raise


def _create_collections():
    """Create collections"""
    
    # Document chunks collection
    if not utility.has_collection("document_chunks"):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name="document_id", dtype=DataType.INT64),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        schema = CollectionSchema(fields, "Document chunks for RAG system")
        collection = Collection("document_chunks", schema)
        
        # Create indexes
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200},
        }
        collection.create_index("embedding", index_params)
        collection.load()
    
    # Long term memory collection
    if not utility.has_collection("long_term_memory"):
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name="memory_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="importance_score", dtype=DataType.FLOAT),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        schema = CollectionSchema(fields, "Long term memory for RAG system")
        collection = Collection("long_term_memory", schema)
        
        # Create indexes
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200},
        }
        collection.create_index("embedding", index_params)
        collection.load()


def get_collection(name: str) -> Collection:
    """Get Milvus collection"""
    if not utility.has_collection(name):
        raise ValueError(f"Collection {name} does not exist")
    
    collection = Collection(name)
    collection.load()
    return collection


def insert_chunks(
    ids: List[str],
    document_ids: List[int],
    chunk_indices: List[int],
    embeddings: List[List[float]],
    sparse_embeddings: List[Dict[int, float]],
    contents: List[str],
    metadatas: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Insert document chunks into Milvus"""
    collection = get_collection("document_chunks")
    
    entities = [
        ids,
        document_ids,
        chunk_indices,
        embeddings,
        sparse_embeddings,
        contents,
        metadatas,
    ]
    
    result = collection.insert(entities)
    collection.flush()
    
    return {
        "insert_count": result.insert_count,
        "primary_keys": result.primary_keys,
    }


def search_chunks(
    query_embedding: List[float],
    query_sparse_embedding: Optional[Dict[int, float]] = None,
    top_k: int = 10,
    document_ids: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """Search document chunks in Milvus"""
    collection = get_collection("document_chunks")
    
    # Build search parameters
    search_params = {
        "metric_type": "COSINE",
        "params": {"ef": 200},
    }
    
    # Build output fields
    output_fields = ["document_id", "chunk_index", "content", "metadata"]
    
    # Search
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=output_fields,
    )
    
    # Format results
    formatted_results = []
    for hits in results:
        for hit in hits:
            result = {
                "id": hit.id,
                "score": hit.score,
                "document_id": hit.entity.get("document_id"),
                "chunk_index": hit.entity.get("chunk_index"),
                "content": hit.entity.get("content"),
                "metadata": hit.entity.get("metadata"),
            }
            formatted_results.append(result)
    
    return formatted_results


def delete_document_chunks(document_id: int) -> Dict[str, Any]:
    """Delete all chunks for a document"""
    collection = get_collection("document_chunks")
    
    expr = f'document_id == {document_id}'
    result = collection.delete(expr)
    collection.flush()
    
    return {
        "delete_count": result.delete_count,
    }


def check_milvus_connection() -> bool:
    """Check if Milvus connection is alive"""
    try:
        connections.get_connection_addr("default")
        return True
    except Exception:
        return False