#!/bin/bash
# Run code quality checks

set -e

echo "🔍 Running code quality checks..."

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

# Run flake8 for style and error checking
run_tool flake8 backend/ main.py --max-line-length=88 --extend-ignore=E203,W503

# Run mypy for type checking
run_tool mypy backend/ main.py --config-file pyproject.toml

echo "✅ All quality checks passed!"