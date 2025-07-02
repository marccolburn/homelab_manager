#!/bin/bash
# Development script to run the backend with the new structure

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the project root directory (parent of scripts directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -f ".venv/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements/backend.txt" ]; then
        .venv/bin/pip install -r requirements/backend.txt
    elif [ -f "requirements-backend.txt" ]; then
        .venv/bin/pip install -r requirements-backend.txt
    else
        echo "❌ Could not find backend requirements file"
        exit 1
    fi
fi

# Set Python path to include project root directory
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Set environment variables for clab-tools
# CLAB_TOOLS_PASSWORD should be set in the environment
echo "CLAB_TOOLS_PASSWORD is $([ -n "$CLAB_TOOLS_PASSWORD" ] && echo "set" || echo "NOT set")"

# Run the Flask backend
echo "Starting Flask backend on http://localhost:5000"
.venv/bin/python -m src.backend.app