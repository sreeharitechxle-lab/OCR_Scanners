from app import app

# Vercel serverless function entry point
# This wraps your Flask app for Vercel's serverless environment

def handler(request):
    """
    Vercel serverless function handler
    """
    return app(request.environ, lambda status, headers: None)

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
