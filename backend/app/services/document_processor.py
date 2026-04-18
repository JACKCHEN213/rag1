"""
Document Processing Service
"""

import asyncio
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

import aiofiles
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.mysql import get_db
from app.database.milvus import insert_chunks
from app.models.document import Document, DocumentChunk
from app.services.embedding_service import generate_embeddings_batch
from app.utils.document_parser import DocumentParser


async def process_document_task(document_id: int, db: Session):
    """
    Process a document: extract text, create chunks, generate embeddings
    """
    print(f"Starting document processing for ID: {document_id}")
    
    try:
        # Get document
        document = db.get(Document, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Update status
        document.status = "processing"
        db.add(document)
        db.commit()
        
        # Parse document
        parser = DocumentParser()
        file_path = Path(document.file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract content
        print(f"Extracting content from {file_path}")
        elements = await parser.parse_document(file_path)
        
        if not elements:
            raise ValueError("No content extracted from document")
        
        print(f"Extracted {len(elements)} elements")
        
        # Create chunks
        chunks = await create_chunks_from_elements(document_id, elements, db)
        print(f"Created {len(chunks)} chunks")
        
        # Generate embeddings
        await generate_embeddings_for_chunks(chunks, db)
        
        # Update document status
        document.status = "completed"
        document.total_chunks = len(chunks)
        db.add(document)
        db.commit()
        
        print(f"Document processing completed: {document_id}")
        
        return {
            "document_id": document_id,
            "total_chunks": len(chunks),
            "status": "completed",
        }
        
    except Exception as e:
        print(f"Document processing failed: {e}")
        
        # Update document status
        document = db.get(Document, document_id)
        if document:
            document.status = "failed"
            db.add(document)
            db.commit()
        
        raise


async def create_chunks_from_elements(
    document_id: int, 
    elements: List[Dict[str, Any]], 
    db: Session
) -> List[DocumentChunk]:
    """Create chunks from parsed elements"""
    
    chunks = []
    current_chunk = []
    current_length = 0
    chunk_index = 0
    
    for element in elements:
        element_type = element.get("type", "text")
        content = element.get("content", "")
        page_number = element.get("page_number")
        coordinates = element.get("coordinates")
        
        # Skip empty content
        if not content or not content.strip():
            continue
        
        # Handle tables and images as separate chunks
        if element_type in ["table", "image"]:
            # Save current chunk if exists
            if current_chunk:
                chunk = create_chunk_from_elements(
                    document_id, chunk_index, current_chunk, db
                )
                chunks.append(chunk)
                chunk_index += 1
                current_chunk = []
                current_length = 0
            
            # Create chunk for table/image
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_index,
                content=content,
                page_number=page_number,
                coordinates=coordinates,
                chunk_type=element_type,
                metadata_={
                    "element_type": element_type,
                    "references": element.get("references", []),
                },
            )
            db.add(chunk)
            chunks.append(chunk)
            chunk_index += 1
            
        else:  # text
            # Check if we need to start a new chunk
            chunk_size = settings.CHUNK_SIZE
            chunk_overlap = settings.CHUNK_OVERLAP
            
            if current_length + len(content) > chunk_size and current_chunk:
                # Save current chunk
                chunk = create_chunk_from_elements(
                    document_id, chunk_index, current_chunk, db
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk with overlap
                if chunk_overlap > 0:
                    overlap_text = "\n".join([
                        c.get("content", "") 
                        for c in current_chunk[-2:]
                    ])[-chunk_overlap:]
                    current_chunk = [
                        {"type": "text", "content": overlap_text}
                    ]
                    current_length = len(overlap_text)
                else:
                    current_chunk = []
                    current_length = 0
            
            # Add to current chunk
            current_chunk.append(element)
            current_length += len(content)
    
    # Save final chunk
    if current_chunk:
        chunk = create_chunk_from_elements(
            document_id, chunk_index, current_chunk, db
        )
        chunks.append(chunk)
    
    db.commit()
    
    return chunks


def create_chunk_from_elements(
    document_id: int,
    chunk_index: int,
    elements: List[Dict[str, Any]],
    db: Session,
) -> DocumentChunk:
    """Create a chunk from elements"""
    
    # Combine content
    content_parts = []
    page_numbers = set()
    metadata = {
        "elements": [],
        "references": [],
    }
    
    for element in elements:
        content = element.get("content", "")
        if content and content.strip():
            content_parts.append(content)
            
            page_number = element.get("page_number")
            if page_number:
                page_numbers.add(page_number)
            
            metadata["elements"].append({
                "type": element.get("type", "text"),
                "page_number": page_number,
                "coordinates": element.get("coordinates"),
            })
            
            references = element.get("references", [])
            if references:
                metadata["references"].extend(references)
    
    content = "\n\n".join(content_parts)
    
    # Create chunk
    chunk = DocumentChunk(
        document_id=document_id,
        chunk_index=chunk_index,
        content=content,
        page_number=min(page_numbers) if page_numbers else None,
        chunk_type="text",
        metadata_=metadata,
    )
    
    db.add(chunk)
    
    return chunk


async def generate_embeddings_for_chunks(
    chunks: List[DocumentChunk],
    db: Session,
):
    """Generate embeddings for chunks"""
    
    if not chunks:
        return
    
    print(f"Generating embeddings for {len(chunks)} chunks")
    
    # Prepare content for embedding
    contents = [chunk.content for chunk in chunks]
    
    # Generate embeddings in batches
    batch_size = settings.EMBEDDING_BATCH_SIZE
    all_embeddings = []
    all_sparse_embeddings = []
    
    for i in range(0, len(contents), batch_size):
        batch = contents[i : i + batch_size]
        batch_chunks = chunks[i : i + batch_size]
        
        # Generate embeddings
        embeddings, sparse_embeddings = await generate_embeddings_batch(batch)
        all_embeddings.extend(embeddings)
        all_sparse_embeddings.extend(sparse_embeddings)
        
        # Update chunk embedding IDs
        for j, chunk in enumerate(batch_chunks):
            embedding_id = str(uuid.uuid4())
            chunk.embedding_id = embedding_id
            db.add(chunk)
        
        db.commit()
        print(f"Processed batch {i//batch_size + 1}")
    
    # Insert into Milvus
    ids = [chunk.embedding_id for chunk in chunks]
    document_ids = [chunk.document_id for chunk in chunks]
    chunk_indices = [chunk.chunk_index for chunk in chunks]
    metadatas = [chunk.metadata_ or {} for chunk in chunks]
    
    result = insert_chunks(
        ids=ids,
        document_ids=document_ids,
        chunk_indices=chunk_indices,
        embeddings=all_embeddings,
        sparse_embeddings=all_sparse_embeddings,
        contents=contents,
        metadatas=metadatas,
    )
    
    print(f"Inserted {result['insert_count']} vectors into Milvus")


def extract_references(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract figure/table references from elements"""
    references = []
    
    for element in elements:
        content = element.get("content", "")
        if not content:
            continue
        
        # Find patterns like "图如-xxx", "如表-xxx", "如图 xxx", etc.
        patterns = [
            r"图\s*如\s*[-\u2013]\s*(\d+)",
            r"如\s*表\s*[-\u2013]\s*(\d+)",
            r"如\s*图\s*[-\u3]\s*(\d+)",
            r"[图表]\s*(\d+)",
            r"图\s+(\d+)",
            r"表\s+(\d+)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                ref_number = match.group(1)
                ref_type = "figure" if "图" in match.group(0) else "table"
                
                references.append({
                    "type": ref_type,
                    "number": ref_number,
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "content_preview": content[max(0, match.start()-20):match.end()+20],
                })
    
    return references