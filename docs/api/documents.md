# Documents API

## Overview

The Documents API provides endpoints for document upload, management, retrieval, and processing.

## Base URL

```
http://localhost:8000/api/documents
```

## Endpoints

### Upload Document

**POST** `/upload`

Upload a document for processing.

**Request:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.pdf"
```

**Response (201 Created):**
```json
{
  "document_id": 123,
  "filename": "document.pdf",
  "status": "pending",
  "message": "Document uploaded successfully, processing started"
}
```

**Supported Formats:**
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx)
- Markdown (.md, .markdown)
- Text (.txt)
- Images (.jpg, .png) (via OCR)

**Error Responses:**
- `400 Bad Request` - Invalid file format
- `413 Payload Too Large` - File size exceeds limit
- `500 Internal Server Error` - Server error during upload

### Get Document List

**GET** `/list`

Retrieve paginated list of documents.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20)

**Request:**
```bash
curl http://localhost:8000/api/documents/list?page=1&page_size=20
```

**Response (200 OK):**
```json
{
  "documents": [
    {
      "id": 123,
      "filename": "document.pdf",
      "original_name": "My Document.pdf",
      "file_path": "uploads/abc123.pdf",
      "file_size": 1024567,
      "file_type": ".pdf",
      "status": "completed",
      "total_chunks": 45,
      "metadata": {
        "content_type": "application/pdf",
        "upload_time": "1234567890.0"
      },
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:05:00"
    }
  ],
  "total": 1
}
```

### Get Document Details

**GET** `/{document_id}`

Get detailed information about a specific document.

**Request:**
```bash
curl http://localhost:8000/api/documents/123
```

**Response (200 OK):**
```json
{
  "document": {
    "id": 123,
    "filename": "document.pdf",
    "original_name": "My Document.pdf",
    "file_path": "uploads/abc123.pdf",
    "file_size": 1024567,
    "file_type": ".pdf",
    "status": "completed",
    "total_chunks": 45,
    "metadata": {...},
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:05:00"
  },
  "chunk_count": 45
}
```

**Error Responses:**
- `404 Not Found` - Document not found

### Get Document Chunks

**GET** `/{document_id}/chunks`

Retrieve chunks for a specific document with pagination.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 50)

**Request:**
```bash
curl http://localhost:8000/api/documents/123/chunks?page=1&page_size=50
```

**Response (200 OK):**
```json
[
  {
    "id": 456,
    "document_id": 123,
    "chunk_index": 0,
    "content": "This is the first chunk of the document...",
    "page_number": 1,
    "chunk_type": "text",
    "metadata": {
      "element_type": "text",
      "page_number": 1,
      "references": []
    }
  },
  {
    "id": 457,
    "document_id": 123,
    "chunk_index": 1,
    "content": "| Column 1 | Column 2 |\n|----------|----------|\n| Data 1   | Data 2   |",
    "page_number": 2,
    "chunk_type": "table",
    "metadata": {
      "element_type": "table",
      "page_number": 2,
      "coordinates": {"x": 100, "y": 200, "width": 400, "height": 300}
    }
  }
]
```

### Update Chunk

**PUT** `/chunks/{chunk_id}`

Update the content of a document chunk.

**Request:**
```bash
curl -X PUT http://localhost:8000/api/documents/chunks/456 \
  -F "content=Updated chunk content here..."
```

**Response (200 OK):**
```json
{
  "message": "Chunk updated successfully",
  "chunk": {
    "id": 456,
    "document_id": 123,
    "chunk_index": 0,
    "content": "Updated chunk content here...",
    "page_number": 1,
    "chunk_type": "text",
    "metadata": {...}
  }
}
```

**Error Responses:**
- `404 Not Found` - Chunk not found
- `400 Bad Request` - Invalid content

### Reprocess Document

**POST** `/{document_id}/reprocess`

Reprocess a document (useful after making changes to chunking or processing logic).

**Request:**
```bash
curl -X POST http://localhost:8000/api/documents/123/reprocess
```

**Response (200 OK):**
```json
{
  "message": "Reprocessing started",
  "task_id": "abc-123-def-456"
}
```

### Delete Document

**DELETE** `/{document_id}`

Delete a document and all its associated chunks.

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/documents/123
```

**Response (200 OK):**
```json
{
  "document_id": 123,
  "message": "Document 'My Document.pdf' deleted successfully"
}
```

### Get Document Statistics

**GET** `/stats`

Get statistics about document collection.

**Request:**
```bash
curl http://localhost:8000/api/documents/stats
```

**Response (200 OK):**
```json
{
  "total_documents": 156,
  "status_breakdown": {
    "pending": 2,
    "processing": 1,
    "completed": 150,
    "failed": 3
  },
  "total_chunks": 4250,
  "file_types": {
    ".pdf": 89,
    ".docx": 34,
    ".md": 25,
    ".xlsx": 8
  }
}
```

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error status codes:
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - Request too large
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limiting

API endpoints may have rate limits applied in production. Check response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with these parameters:

- `page`: Page number (starts at 1)
- `page_size`: Number of items per page

Response headers include pagination info:

```
X-Total-Count: 156
X-Total-Pages: 8
X-Current-Page: 1
```

## WebSocket Support

For real-time updates during document processing, use WebSocket connection:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/document/{task_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
};
```
