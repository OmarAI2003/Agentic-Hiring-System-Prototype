"""
Simple script to start the onboarding form server
Run this to make the form available at http://localhost:5000/onboarding
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from python.onboarding.web_form import app, logger

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.getenv('PORT', 5000))
    
    print("=" * 60)
    print("ONBOARDING FORM SERVER")
    print("=" * 60)
    print(f"Server starting on: http://127.0.0.1:{port}")
    print(f"Form URL: http://127.0.0.1:{port}/onboarding")
    print("Access this URL from your emails to fill the form")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nForm server stopped")
