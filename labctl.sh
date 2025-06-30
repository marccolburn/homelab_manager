#!/bin/bash
# labctl CLI wrapper - calls the Python CLI with the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
CLI_MODULE="$SCRIPT_DIR/labctl.py"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Please run the setup first:"
    echo "  cd $SCRIPT_DIR"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if CLI module exists
if [ ! -f "$CLI_MODULE" ]; then
    echo "Error: labctl.py not found at $CLI_MODULE"
    exit 1
fi

# Execute the CLI with all arguments passed through
exec "$VENV_PYTHON" "$CLI_MODULE" "$@"