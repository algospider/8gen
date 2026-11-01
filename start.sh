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

# Load .env if present
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs) > /dev/null 2>&1 || true
fi

if [ -n "$GEMINI_API_KEY" ]; then
    echo "⚡ Engine: Google Gemini API (Ultra-fast generation mode active)"
else
    echo "ℹ️ Engine: Local Ollama (Set GEMINI_API_KEY for 100x faster generation)"
fi

# Launch 8Gen
python3 -m eightgen "$@"
