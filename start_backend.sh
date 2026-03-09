#!/bin/bash

# Netrikan Backend Startup Script
# Date: 9 March 2026

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🚀 STARTING NETRIKAN BACKEND SERVER 🚀               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project root
cd "/Users/bighnesh/Desktop/Netrikan copy"

# Activate virtual environment
echo "✓ Activating Python virtual environment..."
source .venv/bin/activate

# Navigate to backend
cd backend

# Start server
echo "✓ Starting FastAPI server on http://localhost:8000"
echo "✓ Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the server
python main.py
