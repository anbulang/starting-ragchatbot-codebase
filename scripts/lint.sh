#!/bin/bash
# Run code quality checks

set -e

echo "🔍 Running code quality checks..."

# Run flake8 for style and error checking
echo "Running flake8..."
uv run flake8 backend/ main.py --max-line-length=88 --extend-ignore=E203,W503

# Run mypy for type checking
echo "Running mypy..."
uv run mypy backend/ main.py --config-file pyproject.toml

echo "✅ All quality checks passed!"