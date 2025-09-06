#!/bin/bash
# Format code with black and isort

set -e

echo "🔧 Formatting Python code..."

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

# Format with black
run_tool black . --config pyproject.toml

# Sort imports with isort
run_tool isort . --settings-path pyproject.toml

echo "✅ Code formatting complete!"