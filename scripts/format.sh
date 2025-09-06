#!/bin/bash
# Format code with black and isort

set -e

echo "🔧 Formatting Python code..."

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Format with black
echo "Running black formatter..."
uv run black . --config pyproject.toml

# Sort imports with isort
echo "Sorting imports with isort..."
uv run isort . --settings-path pyproject.toml

echo "✅ Code formatting complete!"