#!/bin/bash
# Format code using Docker

set -e

echo "🔧 Formatting Python code using Docker..."

# Build the image if it doesn't exist
if ! docker image inspect rag-chatbot:latest >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t rag-chatbot .
fi

# Run formatting in container
docker run --rm -v "$(pwd):/app" -w /app rag-chatbot:latest bash -c "
    echo 'Running black formatter...'
    uv run black . --config pyproject.toml
    
    echo 'Sorting imports with isort...'
    uv run isort . --settings-path pyproject.toml
    
    echo 'Code formatting complete!'
"

echo "✅ Code formatting complete!"