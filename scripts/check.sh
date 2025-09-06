#!/bin/bash
# Quick check without modifying files - for CI/CD

set -e

echo "🔍 Running quality checks (no modifications)..."

# Check formatting with black (don't modify)
echo "Checking black formatting..."
uv run black --check --diff . --config pyproject.toml

# Check import sorting (don't modify)
echo "Checking import sorting..."
uv run isort --check-only --diff . --settings-path pyproject.toml

# Run flake8
echo "Running flake8..."
uv run flake8 backend/ main.py --max-line-length=88 --extend-ignore=E203,W503

# Run mypy
echo "Running mypy..."
uv run mypy backend/ main.py --config-file pyproject.toml

echo "✅ All checks passed - code is properly formatted and typed!"