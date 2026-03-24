#!/bin/bash
# Softnet - Double-click to run (macOS/Linux)

set -e
cd "$(dirname "$0")"

echo ""
echo "  ============================"
echo "   Softnet - Network Analysis"
echo "  ============================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "  [ERROR] Python 3 not found. Install Python 3.11+"
    read -p "  Press Enter to exit..."
    exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
    echo "  [ERROR] Node.js not found. Install Node.js 18+"
    read -p "  Press Enter to exit..."
    exit 1
fi

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo "  [1/4] Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install Python deps if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "  [2/4] Installing Python dependencies..."
    pip install -e . -q
fi

# Build frontend if needed
if [ ! -f "frontend/dist/index.html" ]; then
    echo "  [3/4] Installing frontend dependencies..."
    cd frontend && npm install --silent
    echo "  [4/4] Building frontend..."
    npm run build --silent
    cd ..
fi

echo ""
echo "  Starting Softnet..."
echo "  Opening http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

# Open browser
if command -v xdg-open &>/dev/null; then
    (sleep 2 && xdg-open http://localhost:8000) &
elif command -v open &>/dev/null; then
    (sleep 2 && open http://localhost:8000) &
fi

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
