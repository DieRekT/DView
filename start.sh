#!/bin/bash

echo "🔒 Starting Security Camera App..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
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
if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "🚀 Starting server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "💡 Press Ctrl+C to stop the server"
echo ""

cd backend
python3 -c "from app import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')" 