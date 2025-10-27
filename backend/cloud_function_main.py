"""
Cloud Functions entry point for the Pressure Watcher backend.
Cloud Functions Gen 2 can serve FastAPI apps directly.
"""

from main import app

# Export the FastAPI app as the entry point
# Cloud Functions will automatically serve it using uvicorn
__all__ = ['app']
