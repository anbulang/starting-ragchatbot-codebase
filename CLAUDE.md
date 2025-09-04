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
```bash
# Quick start (recommended)
./run.sh

# Manual start
cd backend && uv run uvicorn app:app --reload --port 8000
```

### Key Development Notes

- The system automatically loads documents from the `docs/` folder on startup
- ChromaDB data is persisted in `backend/chroma_db/`
- The RAG system uses tool-based search where Claude can call search functions rather than direct vector similarity
- Sessions are managed in-memory and reset on server restart
- Configuration is centralized in `backend/config.py`
- No test framework is currently configured in this project