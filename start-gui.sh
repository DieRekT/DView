#!/bin/bash

echo "🔒 Starting DualCam Security Monitor GUI..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "backend/gui_with_preview.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/lib/python*/site-packages/opencv_python" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the GUI
echo "🚀 Starting GUI..."
echo "💡 Press Ctrl+C to stop the application"
echo ""

cd backend
python3 gui_with_preview.py 