"""
Desktop launcher for ERP Català using pywebview.
This wraps the FastAPI application in a native window.
"""
import webview
import threading
import uvicorn
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.interface.api.main import app

def start_server():
    """Start the FastAPI server in a separate thread."""
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="error"
    )

def main():
    """Main entry point for the desktop application."""
    # Start the FastAPI server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for the server to start
    import time
    time.sleep(2)
    
    # Create and show the window
    window = webview.create_window(
        'ERP Català',
        'http://127.0.0.1:8000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(1024, 768)
    )
    
    webview.start()

if __name__ == '__main__':
    main()
