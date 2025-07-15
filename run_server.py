#!/usr/bin/env python3
"""
Security Camera App - Launch Script
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import cv2
        import numpy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_camera():
    """Check if camera is available"""
    try:
        import cv2
        cap = cv2.VideoCapture(3)
        if cap.isOpened():
            print("✅ Camera detected and accessible")
            cap.release()
            return True
        else:
            print("❌ No camera found at index 3")
            return False
    except Exception as e:
        print(f"❌ Camera error: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['recordings', 'events', 'frontend']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Security Camera App...")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir('backend')
    
    # Start the server
    try:
        import uvicorn
        from app import app
        
        print("📡 Server starting on http://localhost:8000")
        print("📹 Camera feed: http://localhost:8000/video_feed")
        print("📁 Recordings: http://localhost:8000/recordings")
        print("\n💡 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🔒 Security Camera App")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists('backend/app.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check camera
    if not check_camera():
        print("⚠️  Camera not available. The app may not work properly.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 
