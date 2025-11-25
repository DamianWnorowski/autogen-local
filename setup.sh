#!/bin/bash
# Setup script for autogen-local
# Run this once to get everything ready

set -e

echo "Setting up autogen-local..."

# Check if ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed"
fi

# Start ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Pull the default model
echo "Pulling mistral model (this may take a while)..."
ollama pull mistral

# Create python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo ""
echo "Setup complete!"
echo ""
echo "To get started:"
echo "  source venv/bin/activate"
echo "  python main.py --help"
echo ""
echo "Quick test:"
echo "  python main.py chat"
echo ""
