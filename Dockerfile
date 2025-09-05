# Use Python 3.13 slim image for better compatibility with PyTorch/sentence-transformers
FROM python:3.13-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy only backend code and necessary files (not frontend for development)
COPY backend ./backend
COPY docs ./docs
COPY .env* ./
COPY README.md ./
COPY main.py ./

# Create necessary directories for ChromaDB and frontend (for volume mounting)
RUN mkdir -p /app/backend/chroma_db /app/frontend && \
    chmod -R 755 /app/backend/chroma_db /app/frontend

# Expose port
EXPOSE 8000

# Set working directory to backend for running the app
WORKDIR /app/backend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/courses || exit 1

# Run the FastAPI application with hot reload for development
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]