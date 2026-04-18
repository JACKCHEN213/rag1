"""
Search API Routes
Handles vector search and document retrieval
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class SearchRequest(BaseModel):
    """Search request"""
    query: str
    top_k: int = 10
    document_id: Optional[int] = None  # Optional: search in specific document
    min_score: float = 0.0
    search_type: str = "hybrid"  # "dense", "sparse", "hybrid"


class SearchResult(BaseModel):
    """Search result"""
    chunk_id: str
    document_id: int
    content: str
    score: float
    page_number: Optional[int]
    metadata: Dict


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[SearchResult]
    total: int
    search_type: str
    took_ms: int


# Demo search results
_demo_chunks = [
    {
        "chunk_id": "chunk_1",
        "document_id": 1,
        "content": "This is a demo chunk about machine learning and AI.",
        "score": 0.95,
        "page_number": 1,
        "metadata": {"source": "demo"}
    },
    {
        "chunk_id": "chunk_2",
        "document_id": 1,
        "content": "Another chunk about neural networks and deep learning.",
        "score": 0.87,
        "page_number": 2,
        "metadata": {"source": "demo"}
    },
    {
        "chunk_id": "chunk_3",
        "document_id": 2,
        "content": "Information about natural language processing techniques.",
        "score": 0.72,
        "page_number": 5,
        "metadata": {"source": "demo"}
    }
]


@router.post("/retrieve", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search documents using vector similarity"""
    # For demo purposes, return mock results
    # In production, this would query Milvus vector database
    
    filtered_results = [
        chunk for chunk in _demo_chunks
        if request.query.lower() in chunk["content"].lower() or request.query == "demo"
    ]
    
    # Filter by document_id if specified
    if request.document_id:
        filtered_results = [
            r for r in filtered_results
            if r["document_id"] == request.document_id
        ]
    
    # Apply min_score filter
    filtered_results = [
        r for r in filtered_results
        if r["score"] >= request.min_score
    ]
    
    # Take top_k
    results = filtered_results[:request.top_k]
    
    return SearchResponse(
        query=request.query,
        results=[SearchResult(**result) for result in results],
        total=len(results),
        search_type=request.search_type,
        took_ms=10  # Demo response time
    )


@router.get("/vector/health")
async def check_vector_db_health():
    """Check vector database health"""
    return {
        "status": "healthy",
        "database": "Milvus",
        "collections": 2,  # document_chunks and long_term_memory
        "connected": True
    }


@router.get("/rerank")
async def rerank_results(
    query: str = Query(..., description="Query string"),
    results: List[int] = Query(default=[]),
    top_n: int = Query(default=5, le=20)
):
    """Rerank search results using cross-encoder"""
    # Demo reranking
    reranked = [
        {"chunk_id": f"chunk_{i}", "score": 0.9 - (i * 0.05), "rank": i + 1}
        for i in range(min(top_n, len(results)))
    ]
    
    return {
        "query": query,
        "reranked": reranked,
        "model": "BGE-Reranker"
    }


@router.post("/hybrid")
async def hybrid_search(
    dense_query: str,
    sparse_query: str,
    weights: Dict[str, float] = None
):
    """Perform hybrid search (dense + sparse)"""
    if weights is None:
        weights = {"dense": 0.5, "sparse": 0.5}
    
    # Demo hybrid search
    dense_results = await search_documents(SearchRequest(query=dense_query))
    sparse_results = await search_documents(SearchRequest(query=sparse_query))
    
    # Combine results (simplified)
    all_results = {}
    
    for result in dense_results.results:
        all_results[result.chunk_id] = {
            "chunk": result,
            "dense_score": result.score,
            "sparse_score": 0
        }
    
    for result in sparse_results.results:
        if result.chunk_id in all_results:
            all_results[result.chunk_id]["sparse_score"] = result.score * 0.8
        else:
            all_results[result.chunk_id] = {
                "chunk": result,
                "dense_score": 0,
                "sparse_score": result.score * 0.8
            }
    
    # Calculate hybrid scores
    hybrid_results = []
    for chunk_data in all_results.values():
        hybrid_score = (
            weights["dense"] * chunk_data["dense_score"] +
            weights["sparse"] * chunk_data["sparse_score"]
        )
        chunk = chunk_data["chunk"]
        chunk.score = hybrid_score
        hybrid_results.append(chunk)
    
    # Sort by hybrid score
    hybrid_results.sort(key=lambda x: x.score, reverse=True)
    
    return SearchResponse(
        query=f"Dense: {dense_query}, Sparse: {sparse_query}",
        results=hybrid_results[:10],
        total=len(hybrid_results),
        search_type="hybrid",
        took_ms=25
    )


@router.get("/collections")
async def list_collections():
    """List vector database collections"""
    return {
        "collections": [
            {
                "name": "document_chunks",
                "type": "vector",
                "dimension": 1024,
                "count": 1250,
                "indexed": True
            },
            {
                "name": "long_term_memory",
                "type": "vector",
                "dimension": 1024,
                "count": 50,
                "indexed": True
            }
        ]
    }
