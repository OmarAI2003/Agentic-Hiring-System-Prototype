"""
Start MCQ Form Server
Run this to enable candidates to take MCQ assessments
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from python.questions.mcq_form_server import app

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.getenv('PORT', 5001))
    
    print("=" * 60)
    print("MCQ FORM SERVER")
    print("=" * 60)
    print(f"Server starting on: http://127.0.0.1:{port}")
    print(f"MCQ Form URL: http://127.0.0.1:{port}/mcq")
    print("Candidates will receive this URL via email")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nMCQ Form server stopped")
