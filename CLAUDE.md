# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Course Materials RAG (Retrieval-Augmented Generation) system that enables intelligent querying of course documents. The system uses ChromaDB for vector storage, Anthropic's Claude for AI responses, and provides a web interface for user interaction.

## Architecture

The application follows a modular backend architecture with the following core components:

- **RAGSystem** (`backend/rag_system.py`): Main orchestrator that coordinates all components
- **DocumentProcessor** (`backend/document_processor.py`): Processes course documents into chunks
- **VectorStore** (`backend/vector_store.py`): ChromaDB interface for semantic search
- **AIGenerator** (`backend/ai_generator.py`): Claude API integration with tool support
- **SessionManager** (`backend/session_manager.py`): Manages conversation history
- **ToolManager/CourseSearchTool** (`backend/search_tools.py`): Tool-based search functionality
- **Models** (`backend/models.py`): Data classes for Course, Lesson, and CourseChunk

The frontend is a simple HTML/CSS/JavaScript interface served statically by FastAPI.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Create .env file with:
ANTHROPIC_API_KEY=your_api_key_here
```

### Running the Application

#### Native (requires Python 3.13+)
```bash
# Quick start (recommended)
./run.sh

# Manual start
cd backend && uv run uvicorn app:app --reload --port 8000
```

#### Docker (recommended for macOS Intel compatibility)
```bash
# Copy environment file and add your API key
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY

# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t rag-chatbot .
docker run -p 8000:8000 --env-file .env rag-chatbot
```

### Code Quality Tools

The project includes comprehensive code quality tools for maintaining consistent code style and catching issues early:

#### Available Quality Tools
- **Black**: Code formatter for consistent Python style (88 character line length)
- **isort**: Import sorter to organize imports consistently
- **flake8**: Style guide enforcement and error checking
- **mypy**: Static type checker for Python

#### Usage Commands

**Using Makefile (recommended):**
```bash
# Show all available commands
make help

# Format code (black + isort)
make format              # Native (requires local tools)
make format-docker       # Using Docker (recommended)

# Run linting (flake8 + mypy)
make lint                # Native
make lint-docker         # Using Docker (recommended)

# Check formatting without modifying files
make check

# Complete quality workflow (format + lint + test)
make quality

# Run tests only
make test

# Clean temporary files
make clean
```

**Using Scripts Directly:**
```bash
# Format code
./scripts/format.sh         # Native
./scripts/format-docker.sh  # Docker

# Run linting
./scripts/lint.sh           # Native  
./scripts/lint-docker.sh    # Docker

# Check without modifying
./scripts/check.sh

# Complete workflow
./scripts/quality.sh
```

#### Docker-Based Quality Checks (Recommended)

Since the project uses Docker and some dependencies can have platform-specific issues, Docker-based quality checks are recommended:

```bash
# Format code using Docker
make format-docker

# Run all quality checks using Docker
make lint-docker
```

#### Configuration

Quality tools are configured in `pyproject.toml`:
- **Black**: 88 character line length, Python 3.13 target
- **isort**: Black-compatible profile with project-specific import grouping
- **mypy**: Strict type checking with external library overrides
- **flake8**: 88 character line length, ignoring Black-incompatible rules (E203, W503)

### Key Development Notes

- The system automatically loads documents from the `docs/` folder on startup
- ChromaDB data is persisted in `backend/chroma_db/`
- The RAG system uses tool-based search where Claude can call search functions rather than direct vector similarity
- Sessions are managed in-memory and reset on server restart
- Configuration is centralized in `backend/config.py`
- No test framework is currently configured in this project
- 使用的docker启动的该项目,后续添加依赖都从dockerfile中添加