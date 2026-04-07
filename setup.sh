#!/bin/bash

echo "========================================="
echo "Multimodal Audio Recognition - Setup"
echo "========================================="
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
echo ""
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Found: Node $NODE_VERSION"
else
    echo "✗ Node.js not found. Please install Node.js 14+"
    exit 1
fi

# Backend setup
echo ""
echo "========================================="
echo "Setting up Backend"
echo "========================================="
echo "Installing backend dependencies..."
pip install -r backend_requirements.txt

if [ ! -f "saved_model/audio_model_full.h5" ] && [ ! -f "saved_model/audio_model.h5" ] && [ ! -f "saved_model/audio_model.pt" ]; then
    echo "⚠ Warning: Model file not found in saved_model/"
    echo "  Expected one of: audio_model_full.h5, audio_model.h5, audio_model.pt"
fi

# Frontend setup
echo ""
echo "========================================="
echo "Setting up Frontend"
echo "========================================="
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To run the application:"
echo ""
echo "1. Start Backend (in project root):"
echo "   python backend/app.py"
echo ""
echo "2. Start Frontend (in another terminal):"
echo "   cd frontend && npm start"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
