#!/usr/bin/env python3
"""
Run test server for interactive testing
Usage: python run_test_server.py
"""

import os
import sys
import threading
import time
from app import create_app
from dotenv import load_dotenv

def main():
    # Load environment
    load_dotenv()
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ No OPENAI_API_KEY found in .env file!")
        return
    
    # Create app
    app = create_app('development')
    
    print("🚀 Starting Quote Speak App Test Server...")
    print("📱 Open your browser to: http://localhost:5555")
    print("🛑 Press Ctrl+C to stop")
    print("\n🧪 Test Cases to Try:")
    print("1. Short text: 'Hello world!'")
    print("2. Medium text: 'This is a medium length quote that should wrap nicely across multiple lines.'")
    print("3. Long text: 'This is a very long quote that will test the automatic font sizing and text wrapping features...'")
    print("4. Multiple paragraphs: Use \\n\\n to separate paragraphs")
    print("\n" + "="*60)
    
    try:
        # Run app
        app.run(host='0.0.0.0', port=5555, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")

if __name__ == '__main__':
    main()