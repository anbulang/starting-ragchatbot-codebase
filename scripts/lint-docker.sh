#!/bin/bash
# Run linting using Docker

set -e

echo "🔍 Running code quality checks using Docker..."

# Build the image if it doesn't exist
if ! docker image inspect rag-chatbot:latest >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t rag-chatbot .
fi

# Run linting in container
docker run --rm -v "$(pwd):/app" -w /app rag-chatbot:latest bash -c "
    echo 'Running flake8...'
    uv run flake8 backend/ main.py --max-line-length=88 --extend-ignore=E203,W503
    
    echo 'Running mypy...'
    uv run mypy backend/ main.py --config-file pyproject.toml
    
    echo 'All quality checks passed!'
"

echo "✅ All quality checks passed!"