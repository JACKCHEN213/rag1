# Contributing to RAG System

Thank you for your interest in contributing to the RAG System! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

- Be kind and respectful to others
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please create an issue on GitHub:

1. Check if the issue already exists
2. Use a clear, descriptive title
3. Provide detailed steps to reproduce (for bugs)
4. Include relevant logs, screenshots, or examples
5. Specify your environment (OS, Python version, etc.)

### Feature Requests

We welcome feature requests! Please:

1. Describe the feature and its use case
2. Explain why it would be valuable
3. Consider if it fits the project's scope
4. Be open to discussion and feedback

### Pull Requests

We love pull requests! Here's how to contribute code:

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/your-username/rag1.git
cd rag1
git remote add upstream https://github.com/JACKCHEN213/rag1.git
```

#### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

Use a descriptive branch name:
- `feature/`: New features
- `fix/`: Bug fixes
- `docs/`: Documentation improvements
- `refactor/`: Code refactoring
- `test/`: Testing improvements

#### 3. Make Changes

- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

#### 4. Test Your Changes

```bash
# Run tests
cd backend
pytest

# Check code formatting
cd backend
black --check app/
isort --check-only app/
flake8 app/
mypy app/

# For frontend
cd frontend
npm run lint
npm run type-check
```

#### 5. Commit Your Changes

We follow conventional commits. Use one of these prefixes:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Build system, dependencies, etc.

```bash
git add .
git commit -m "feat: add new document upload feature

- Support batch upload
- Add progress tracking
- Update API documentation"
```

Include a detailed description in the commit body if needed.

#### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub:

1. Provide a clear title and description
2. Reference any related issues
3. Ensure all checks pass
4. Request review from maintainers

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Ensure tests pass
- Update documentation
- Add tests for new functionality
- Respond to feedback promptly

## Development Setup

### Backend Development

```bash
# Clone repository
git clone https://github.com/JACKCHEN213/rag1.git
cd rag1

# Start databases
docker-compose up -d mysql milvus redis

# Setup backend
cd backend
cp .env.example .env
# Edit .env with your configuration

poetry install
poetry shell

# Run development server
python -m app.main
```

### Frontend Development

```bash
cd frontend
pnpm install
pnpm dev
```

### Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
pnpm test
```

## Coding Standards

### Python (Backend)

- **Formatting**: Use Black with line length 88
- **Imports**: Use isort with black profile
- **Linting**: Use flake8
- **Types**: Include type hints, run mypy
- **Docstrings**: Use Google style docstrings

```python
# Example
def process_document(
    document_id: int,
    processor: DocumentProcessor
) -> ProcessResult:
    """Process a document and extract chunks.

    Args:
        document_id: The ID of the document to process
        processor: The document processor instance

    Returns:
        ProcessResult containing chunks and metadata

    Raises:
        ValueError: If document not found
    """
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Write meaningful tests

### Git Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

Examples:
```
feat: add document chunk editing

- Allow users to modify chunk content
- Update embeddings after changes
- Add UI components for editing

Closes #123
```

```
fix: resolve memory leak in embedding service

The embedding service was not properly releasing GPU memory
after batch processing. Added explicit memory cleanup.

Fixes #456
```

## Documentation

- Update README.md for user-facing changes
- Update API documentation for API changes
- Add inline comments for complex logic
- Update examples and tutorials

## Testing

### Test Requirements

- Write unit tests for new functions
- Add integration tests for new features
- Ensure tests cover edge cases
- Maintain or improve code coverage

### Test Structure

```python
# tests/unit/test_service.py
def test_process_document():
    # Arrange
    doc = create_test_document()
    
    # Act
    result = process_document(doc)
    
    # Assert
    assert result.chunks > 0
    assert result.status == "completed"
```

## Performance Considerations

- Consider memory usage with large documents
- Optimize database queries
- Use batch processing where possible
- Add caching for expensive operations
- Profile performance-critical code

## Security

- Never commit secrets or credentials
- Validate all user inputs
- Use parameterized queries
- Follow security best practices
- Report security issues privately

## Documentation Contributions

### Improving Docs

- Fix typos and grammar errors
- Clarify confusing sections
- Add examples
- Update screenshots
- Translate to other languages

### Adding New Documentation

- Create tutorials for common use cases
- Add API usage examples
- Write troubleshooting guides
- Document architecture decisions

## Community

### Discussion

Participate in discussions:
- GitHub Discussions for general topics
- Issue comments for specific issues
- Code reviews for proposed changes

### Helping Others

- Answer questions in discussions
- Help review pull requests
- Share your experiences
- Report bugs with detailed information

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- Release notes
- Project README (for significant contributions)

## Questions?

If you have questions:
1. Check existing documentation
2. Search existing issues
3. Start a GitHub Discussion
4. Ask in relevant issue/PR

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to the RAG System! 🎉
