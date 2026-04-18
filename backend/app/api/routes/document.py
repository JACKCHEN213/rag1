"""
Document API Routes
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
import asyncio

from app.database.mysql import get_db
from app.database.redis import set_task_status, get_task_status
from app.models.document import (
    Document,
    DocumentChunk,
    DocumentUploadResponse,
    DocumentStatusResponse,
    ChunkResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
)
from app.services.document_processor import process_document_task

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a document"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Get file extension
    ext = Path(file.filename).suffix.lower()
    allowed_extensions = [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".md", ".txt", ".jpg", ".png"]
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Supported types: {', '.join(allowed_extensions)}"
        )
    
    # Create upload directory
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Save file
    file_id = str(uuid.uuid4())
    storage_filename = f"{file_id}{ext}"
    file_path = upload_dir / storage_filename
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create document record
    document = Document(
        filename=storage_filename,
        original_name=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        file_type=ext,
        status="pending",
        metadata_={
            "content_type": file.content_type,
            "upload_time": str(asyncio.get_event_loop().time()),
        },
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Start async processing
    task_id = str(uuid.uuid4())
    asyncio.create_task(process_document_async(document.id, task_id, db))
    
    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.original_name,
        status=document.status,
        message="Document uploaded successfully, processing started",
    )


async def process_document_async(document_id: int, task_id: str, db: Session):
    """Process document asynchronously"""
    try:
        # Update task status
        set_task_status(task_id, "processing")
        
        # Process document
        result = await process_document_task(document_id, db)
        
        # Update task status
        set_task_status(task_id, "completed", result)
        
    except Exception as e:
        set_task_status(task_id, "failed", {"error": str(e)})


@router.get("/status/{task_id}", response_model=DocumentStatusResponse)
async def get_upload_status(task_id: str):
    """Get upload/processing status"""
    status_data = get_task_status(task_id)
    
    if not status_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status_data


@router.get("/list", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """List documents with pagination"""
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Query documents
    query = select(Document).order_by(Document.created_at.desc())
    total = db.exec(select(func.count()).select_from(Document)).one()
    
    query = query.offset(offset).limit(page_size)
    documents = db.exec(query).all()
    
    return DocumentListResponse(
        documents=documents,
        total=total,
    )


@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document details"""
    
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get chunk count
    chunk_count = db.exec(
        select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == document_id)
    ).one()
    
    return {
        "document": document,
        "chunk_count": chunk_count,
    }


@router.get("/{document_id}/chunks", response_model=List[ChunkResponse])
async def get_document_chunks(
    document_id: int,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
):
    """Get document chunks"""
    
    # Check if document exists
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get chunks
    offset = (page - 1) * page_size
    query = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .offset(offset)
        .limit(page_size)
    )
    chunks = db.exec(query).all()
    
    return chunks


@router.put("/chunks/{chunk_id}")
async def update_chunk(
    chunk_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    """Update chunk content"""
    
    chunk = db.get(DocumentChunk, chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Update content
    chunk.content = content
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    
    return {"message": "Chunk updated successfully", "chunk": chunk}


@router.post("/{document_id}/reprocess")
async def reprocess_document(document_id: int, db: Session = Depends(get_db)):
    """Reprocess a document"""
    
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update status
    document.status = "pending"
    db.add(document)
    db.commit()
    
    # Start reprocessing
    task_id = str(uuid.uuid4())
    asyncio.create_task(process_document_async(document.id, task_id, db))
    
    return {"message": "Reprocessing started", "task_id": task_id}


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get filename for response
    filename = document.original_name
    
    # Delete file
    try:
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Warning: Failed to delete file: {e}")
    
    # Delete from database (cascades to chunks)
    db.delete(document)
    db.commit()
    
    # Delete from Milvus
    from app.database.milvus import delete_document_chunks
    try:
        delete_document_chunks(document_id)
    except Exception as e:
        print(f"Warning: Failed to delete from Milvus: {e}")
    
    return DocumentDeleteResponse(
        document_id=document_id,
        message=f"Document '{filename}' deleted successfully",
    )


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get document statistics"""
    
    # Total documents
    total_docs = db.exec(select(func.count()).select_from(Document)).one()
    
    # Documents by status
    status_counts = db.exec(
        select(Document.status, func.count(Document.id)).group_by(Document.status)
    ).all()
    status_data = {status: count for status, count in status_counts}
    
    # Total chunks
    total_chunks = db.exec(select(func.count()).select_from(DocumentChunk)).one()
    
    # File types
    type_counts = db.exec(
        select(Document.file_type, func.count(Document.id))
        .group_by(Document.file_type)
        .where(Document.file_type.isnot(None))
    ).all()
    type_data = {file_type: count for file_type, count in type_counts if file_type}
    
    return {
        "total_documents": total_docs,
        "status_breakdown": status_data,
        "total_chunks": total_chunks,
        "file_types": type_data,
    }