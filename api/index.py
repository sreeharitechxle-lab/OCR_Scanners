"""
Vercel Serverless Function Entry Point
Minimal version to avoid crashes
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ.setdefault('PYTHONUNBUFFERED', '1')

def handler(request):
    """
    Main Vercel serverless function handler
    """
    try:
        # Import Flask app with error handling
        from app import app
        
        # Convert Vercel request to WSGI format
        environ = {
            'REQUEST_METHOD': request.method,
            'PATH_INFO': request.path,
            'SERVER_NAME': 'vercel.app',
            'SERVER_PORT': '443',
            'wsgi.url_scheme': 'https',
            'wsgi.input': request.body,
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Add headers
        for key, value in request.headers.items():
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
        
        # Response collector
        response_data = {}
        def start_response(status, headers):
            response_data['status'] = status
            response_data['headers'] = headers
        
        # Call Flask app
        app_iter = app(environ, start_response)
        response_body = b''.join(app_iter)
        
        return {
            'statusCode': int(response_data.get('status', '200').split()[0]),
            'headers': dict(response_data.get('headers', [])),
            'body': response_body.decode('utf-8')
        }
        
    except Exception as e:
        print(f"❌ Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e),
                'status': 'error'
            })
        }

# For Vercel compatibility
app_handler = handler
