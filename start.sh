#!/usr/bin/env bash
# 8Gen — Instant One-Click Launcher

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo "⚡ Starting 8Gen — Instant AI Game Studio"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3.9+ to continue."
    exit 1
fi

# Check / Setup Virtualenv
if [ ! -d ".venv" ]; then
    echo "📦 Setting up local environment (first-time only)..."
    python3 -m venv .venv
    ./.venv/bin/pip install --upgrade pip > /dev/null 2>&1
    ./.venv/bin/pip install -e . > /dev/null 2>&1
fi

# Activate virtualenv
source .venv/bin/activate

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo ""
    echo "⚠️  Ollama does not appear to be running on http://localhost:11434."
    if command -v ollama &> /dev/null; then
        echo "   Attempting to start Ollama in background..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
    else
        echo "   Please make sure Ollama is installed from https://ollama.com and running."
    fi
fi

# Launch 8Gen Interactive Wizard
python3 -m eightgen "$@"
