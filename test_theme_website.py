#!/usr/bin/env python3
"""
Test the themed website locally
Usage: python test_theme_website.py
"""

import os
import sys
import webbrowser
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
    
    print("🎨 Starting Quote to Speak - Themed Website Test...")
    print("📱 Opening browser to: http://localhost:5555")
    print("🛑 Press Ctrl+C to stop")
    print("\n🎨 Test the Dynamic Theming:")
    print("1. Try different color templates and watch the website change")
    print("2. Purple to Blue - Default elegant theme")
    print("3. Sunset - Warm orange gradient")
    print("4. Ocean - Cool blue theme")
    print("5. Forest - Natural green theme")
    print("6. Dark - Modern dark theme")
    print("\n" + "="*60)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5555')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Run app
        app.run(host='0.0.0.0', port=5555, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")

if __name__ == '__main__':
    main()