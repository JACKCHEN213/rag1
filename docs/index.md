# RAG System Documentation

Welcome to the RAG (Retrieval-Augmented Generation) System documentation!

## Overview

The RAG System is a powerful document retrieval and question-answering platform that combines state-of-the-art natural language processing with efficient vector search capabilities.

## Features

- 📄 **Multi-format Document Support**: PDF, Word, Excel, PPT, Markdown, images
- 🔍 **Intelligent Search**: Hybrid (dense + sparse) vector search with reranking
- 🧠 **Memory Management**: Short-term and long-term memory for context retention
- ⚡ **High Performance**: Optimized vector database with HNSW indexing
- 🎯 **Chinese Optimized**: BGE-M3 embedding model for superior Chinese text understanding
- 🎨 **Modern UI**: Beautiful web interface with real-time interactions
- 🔧 **Flexible Configuration**: Support for multiple LLM providers

## Quick Start

1. Install dependencies and start services:
```bash
docker-compose up -d mysql milvus redis
cd backend
poetry install
python -m app.main
```

2. Access the API:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Documentation Sections

- **[API Reference](api/)**: Complete API documentation
- **[Architecture](architecture/)**: System design and architecture
- **[Configuration](configuration/)**: Configuration options and settings
- **[Deployment](deployment/)**: Deployment guides and best practices
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Getting Help

- Report bugs: [GitHub Issues](https://github.com/JACKCHEN213/rag1/issues)
- Ask questions: [GitHub Discussions](https://github.com/JACKCHEN213/rag1/discussions)
- Contributing: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## License

MIT License - See [LICENSE](../LICENSE)
