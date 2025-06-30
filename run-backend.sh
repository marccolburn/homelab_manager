#!/bin/bash
# Development script to run the backend with the new structure

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

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

# Set Python path to include src directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the Flask backend
echo "Starting Flask backend on http://localhost:5000"
.venv/bin/python -m src.backend.app