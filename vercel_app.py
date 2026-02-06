"""
Vercel-compatible Flask application
This file adapts your Flask app for Vercel's serverless environment
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Set environment variables for Vercel
os.environ.setdefault('PYTHONUNBUFFERED', '1')

# Import your Flask app with error handling
try:
    from app import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    # Create a minimal Flask app as fallback
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error_fallback():
        return jsonify({
            "error": "Failed to import main application",
            "message": str(e),
            "status": "import_error"
        }), 500

# Vercel serverless function handler
def handler(environ, start_response):
    """
    WSGI handler for Vercel serverless functions
    """
    try:
        return app(environ, start_response)
    except Exception as e:
        print(f"❌ Handler error: {e}")
        # Return error response
        start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
        return [json.dumps({"error": "Internal server error", "message": str(e)}).encode()]

# Export for Vercel
app_handler = handler

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
