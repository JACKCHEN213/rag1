# System Architecture

## Overview

The RAG System follows a modern microservices architecture with clear separation between frontend, backend, and infrastructure components.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │   Backend       │     │   Database      │
│   (React)       │────▶│   (FastAPI)     │────▶│   Layer         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      │                        │                        │
      │                        │                        │
      ▼                        ▼                        ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Web UI        │  │   API Routes    │  │   MySQL 8.0     │
│   - Chat        │  │   - Documents   │  │   - Metadata    │
│   - Documents   │  │   - Search      │  │   - Memory      │
│   - Config      │  │   - Memory      │  └─────────────────┘
└─────────────────┘  │   - Chat        │
                     └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   Services      │
                     └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   ML Models     │
                     │   - BGE-M3      │
                     │   - BGE-Reranker│
                     └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   Vector DB     │
                     │   (Milvus)      │
                     └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   Cache         │
                     │   (Redis)       │
                     └─────────────────┘
```

## Components

### 1. Frontend (React + TypeScript)

**Technology Stack:**
- React 18
- TypeScript
- Ant Design
- Zustand (state management)
- Axios (HTTP client)

**Key Features:**
- Responsive design
- Real-time chat interface
- Document management UI
- Configuration panels
- Progress tracking

**Directory Structure:**
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── stores/        # State management
│   ├── utils/         # Utility functions
│   └── App.tsx        # Root component
└── public/            # Static assets
```

### 2. Backend (FastAPI + Python)

**Technology Stack:**
- FastAPI (ASGI framework)
- Python 3.10+
- SQLModel (SQLAlchemy + Pydantic)
- Pydantic Settings
- Celery (async tasks)

**Architecture Pattern:**
- Layered architecture (API, Service, Repository)
- Dependency injection
- Async/await for I/O operations
- Type hints throughout

**Key Components:**

#### API Layer
- RESTful endpoints
- Automatic OpenAPI documentation
- Input validation
- Authentication/Authorization (if added)

#### Service Layer
- Document processing
- Embedding generation
- Search and retrieval
- Memory management
- LLM integration

#### Repository Layer
- Database abstraction
- Vector operations
- Cache management

### 3. Database Layer

#### MySQL 8.0 (Relational Database)
**Purpose:**
- Document metadata
- User data (if added)
- Configuration
- Long-term memory
- Conversation history

**Key Tables:**
- `documents` - Document metadata
- `document_chunks` - Chunk information
- `long_term_memory` - Persistent memory
- `conversations` - Chat history
- `config` - System configuration

#### Milvus 2.x (Vector Database)
**Purpose:**
- Storing embeddings
- Vector similarity search
- Hybrid search capabilities

**Collections:**
- `document_chunks` - Document embeddings
- `long_term_memory` - Memory embeddings

**Index Type:** HNSW (Hierarchical Navigable Small World)
- Optimized for approximate nearest neighbor search
- Balances accuracy and performance

#### Redis (Cache & Session Store)
**Purpose:**
- Short-term memory
- Session management
- Task status tracking
- Rate limiting
- Temporary caching

**Data Structures:**
- Strings (session data)
- Lists (task queues)
- Hashes (configuration)
- Sorted Sets (ranked results)

### 4. Machine Learning Components

#### Embedding Models

**BGE-M3 (BAAI General Embedding)**
- Multi-lingual support (optimized for Chinese)
- Dense and sparse embeddings
- 1024-dimensional vectors
- Supports both retrieval and reranking

**Usage:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-m3')
dense_embedding = model.encode(text, normalize_embeddings=True)
sparse_embedding = model.encode(text, return_sparse=True)
```

#### Reranker Model (BGE-Reranker)
- Cross-encoder architecture
- Re-ranks retrieval results
- Improves relevance accuracy

**Usage:**
```python
pairs = [[query, doc] for doc in documents]
scores = reranker.compute_score(pairs, normalize=True)
```

### 5. Document Processing Pipeline

```
Document Upload
     ↓
Format Detection
     ↓
Content Extraction
     ↓
Text Cleaning
     ↓
Chunking Strategy
     ↓
Embedding Generation
     ↓
Vector Storage (Milvus)
     ↓
Metadata Storage (MySQL)
```

**Supported Formats:**
- PDF (text and scanned)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx)
- Markdown (.md)
- Plain text (.txt)
- Images (.jpg, .png) - via OCR

**Chunking Strategies:**
1. Semantic chunking (using sentence embeddings)
2. Fixed-size chunks with overlap
3. Structure-based (paragraphs, sections)
4. Preserve tables and images

### 6. Search and Retrieval

#### Retrieval Pipeline
```
User Query
     ↓
Query Expansion (optional)
     ↓
Embedding Generation
     ↓
Vector Search (Milvus)
     ↓
Initial Retrieval (Top-K)
     ↓
Reranking (BGE-Reranker)
     ↓
Final Results (Top-N)
     ↓
Context Assembly
     ↓
LLM Generation
```

**Search Types:**
1. **Dense Search**: Semantic similarity
2. **Sparse Search**: Keyword-based (BM25-like)
3. **Hybrid Search**: Weighted combination
4. **Filtered Search**: By metadata, document, date, etc.

**Relevance Scoring:**
```python
final_score = α * dense_score + (1-α) * sparse_score
```

### 7. Memory System

#### Short-term Memory (Redis)
- Recent conversation context
- LRU eviction policy
- Fast access for current session

#### Long-term Memory (MySQL + Milvus)
- Persistent storage
- Importance scoring
- Spaced repetition for retention
- Semantic search capabilities

**Memory Types:**
- `conversation`: Dialogue history
- `document`: Important document excerpts
- `preference`: User preferences
- `entity`: Named entities and facts

**Memory Scoring:**
```python
importance = frequency * recency * relevance
```

### 8. LLM Integration

**Supported Providers:**
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Local models (via vLLM, Ollama)
- Azure OpenAI

**Prompt Template:**
```markdown
System: You are a helpful assistant based on the provided documents.

Context:
{retrieved_chunks}

History:
{conversation_history}

User: {question}

Answer based on the documents above:
```

**Response Streaming:**
- Real-time token generation
- Improved user experience
- Reduced perceived latency

### 9. Configuration Management

**Configuration Sources:**
1. Environment variables
2. Config files (.env)
3. Database settings
4. Runtime parameters

**Configuration Categories:**
- Application settings
- Database connections
- Model parameters
- Processing options
- Search configurations
- Memory settings

### 10. Deployment Architecture

#### Development
```
Local Machine
├── Frontend (hot reload)
├── Backend (reload on change)
├── MySQL (Docker)
├── Milvus (Docker)
└── Redis (Docker)
```

#### Production
```
Kubernetes Cluster
├── Frontend Pods (multiple replicas)
├── Backend Pods (multiple replicas)
├── MySQL Cluster (master-slave)
├── Milvus Cluster
└── Redis Cluster (sentinel)
```

**Load Balancing:**
- Nginx for frontend
- HAProxy for backend
- Milvus internal load balancing

**Monitoring:**
- Prometheus metrics
- Grafana dashboards
- ELK stack for logging

## Data Flow Examples

### 1. Document Upload Flow
```
1. User uploads document via frontend
2. Backend saves file and creates database record
3. Async task queue processes document
4. Document is parsed based on file type
5. Text is split into chunks with metadata
6. Embeddings are generated for each chunk
7. Chunks and embeddings stored in databases
8. Status updated and user notified
```

### 2. Chat Query Flow
```
1. User submits question
2. Question is embedded
3. Vector search retrieves relevant chunks
4. Chunks are reranked for relevance
5. Short-term memory provides context
6. Long-term memory adds relevant info
7. All context is assembled into prompt
8. LLM generates response
9. Response is streamed back to user
10. Memory is updated
```

### 3. Memory Consolidation Flow
```
1. Background process runs periodically
2. Analyzes conversation history
3. Extracts important information
4. Generates embeddings
5. Scores importance
6. Stores in long-term memory
7. Updates existing memories
8. Removes low-importance memories
```

## Performance Considerations

### Optimizations

1. **Batch Processing**
   - Process documents in batches
   - Batch embedding generation
   - Batch database operations

2. **Caching**
   - Cache embeddings
   - Cache search results
   - Cache LLM responses

3. **Index Optimization**
   - HNSW parameters tuning
   - Balanced indexing
   - Query optimization

4. **Async Operations**
   - Non-blocking I/O
   - Concurrent processing
   - Background tasks

### Scaling Strategies

1. **Horizontal Scaling**
   - Multiple backend instances
   - Load balancing
   - Database read replicas

2. **Vertical Scaling**
   - More powerful instances
   - GPU acceleration
   - Increased memory

3. **Database Sharding**
   - Partition by document
   - Partition by tenant
   - Time-based sharding

## Security Considerations

### Current Implementation
- No authentication (for demo purposes)
- File type validation
- Size limits on uploads
- Input sanitization

### Recommended for Production
- Authentication (OAuth2/JWT)
- Authorization (RBAC)
- API rate limiting
- Input validation
- SQL injection prevention
- File scanning (malware)
- HTTPS encryption
- Secure secrets management

## Future Enhancements

### Planned Features
1. Multi-modal support (images, audio, video)
2. Knowledge graph integration
3. Multi-tenant support
4. Advanced document parsing
5. Real-time collaboration
6. Analytics dashboard
7. Plugin system
8. Mobile app
9. API versioning
10. GraphQL interface

### Technical Improvements
1. Graph database integration
2. Distributed training
3. Model quantization
4. Edge deployment
5. Federated search
6. Active learning
7. A/B testing framework
8. Advanced monitoring
9. Auto-scaling
10. Chaos engineering

## Conclusion

The RAG System architecture provides a solid foundation for building enterprise-grade document retrieval and question-answering systems. The modular design allows for easy extension and customization while maintaining performance and reliability.

Key architectural decisions:
- Separation of concerns across layers
- Async-first design for scalability
- Multi-database approach for optimal performance
- ML model abstraction for flexibility
- Modern web framework for developer productivity
