#!/bin/bash

# Netrikan Backend Startup Script
# Updated: 18 March 2026 - Optimized for Python 3.11 Stability

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🚀 STARTING NETRIKAN BACKEND SERVER 🚀               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if uv is installed, if not fallback to pip or inform user
if ! command -v uv &> /dev/null; then
    echo "⚠ uv not found. Falling back to standard pip..."
    # Check if .venv exists, if not create it using Python 3.11
    if [ ! -d ".venv" ]; then
        echo "⚠ Virtual environment (.venv) not found. Creating it with Python 3.11..."
        if command -v python3.11 &> /dev/null; then
            python3.11 -m venv .venv
        else
            echo "❌ Python 3.11 not found in path. Please install it or use python3.10."
            exit 1
        fi
        source .venv/bin/activate
        echo "✓ Upgrading pip..."
        pip install --upgrade pip
        echo "✓ Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "✓ Activating Python virtual environment..."
        source .venv/bin/activate
    fi
else
    echo "✓ uv detected. Using uv for environment management."
    # Check if .venv exists, if not create it using uv
    if [ ! -d ".venv" ]; then
        echo "⚠ Virtual environment (.venv) not found. Creating it with uv..."
        uv venv .venv --python 3.11
        source .venv/bin/activate
        echo "✓ Installing dependencies using uv..."
        uv pip install -r requirements.txt
    else
        echo "✓ Activating Python virtual environment..."
        source .venv/bin/activate
        # Ensure dependencies are up to date with uv
        echo "✓ Syncing dependencies with uv..."
        uv pip install -r requirements.txt
    fi
fi

# Navigate to backend
cd backend

# Start server
echo ""
echo "✓ Project: Netrikan 3-Layer Agentic Architecture"
echo "✓ API: http://localhost:8000"
echo "✓ Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the server
python main.py
