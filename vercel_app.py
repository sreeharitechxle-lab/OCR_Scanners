"""
Vercel-compatible Flask application
This file adapts your Flask app for Vercel's serverless environment
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import your Flask app
from app import app

# Vercel serverless function handler
def handler(environ, start_response):
    """
    WSGI handler for Vercel serverless functions
    """
    return app(environ, start_response)

# Export for Vercel
app_handler = handler

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
