#!/usr/bin/env python3
"""
WSGI entry point for production deployment
This file must contain an 'app' variable for gunicorn to find
"""

from flask import Flask

# Create Flask app directly here - no imports needed
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🌍 UniBabel is Live!</h1>
    <p>Your real-time translation messaging platform is now running on DigitalOcean!</p>
    <p><a href="/health">Health Check</a></p>
    '''

@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'message': 'UniBabel is running successfully!',
        'app': 'UniBabel Translation Platform'
    }

# This ensures gunicorn can find the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)