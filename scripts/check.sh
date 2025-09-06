#!/bin/bash
# Quick check without modifying files - for CI/CD

set -e

echo "🔍 Running quality checks (no modifications)..."

# Function to try running a command with uv, fallback to system
run_tool() {
    local tool=$1
    shift
    echo "Running $tool..."
    
    # Try with uv first
    if uv run --with $tool $tool "$@" 2>/dev/null; then
        return 0
    elif command -v $tool >/dev/null 2>&1; then
        # Fallback to system installation
        echo "Using system $tool..."
        $tool "$@"
    else
        echo "❌ $tool not available. Install with: pip install $tool"
        return 1
    fi
}

# Check formatting with black (don't modify)
run_tool black --check --diff . --config pyproject.toml

# Check import sorting (don't modify)
run_tool isort --check-only --diff . --settings-path pyproject.toml

# Run flake8
run_tool flake8 backend/ main.py --max-line-length=88 --extend-ignore=E203,W503

# Run mypy
run_tool mypy backend/ main.py --config-file pyproject.toml

echo "✅ All checks passed - code is properly formatted and typed!"