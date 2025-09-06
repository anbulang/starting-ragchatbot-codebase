#!/bin/bash
# Complete code quality workflow: format, lint, and test

set -e

echo "🚀 Running complete quality checks..."

# Format code first
echo "Step 1: Formatting code..."
./scripts/format.sh

# Run linting
echo "Step 2: Running linters..."
./scripts/lint.sh

# Run tests
echo "Step 3: Running tests..."
uv run pytest backend/tests/ -v

echo "🎉 All quality checks completed successfully!"