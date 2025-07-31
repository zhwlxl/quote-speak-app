#!/usr/bin/env python3
"""
Local development runner
Usage: python run_local.py
"""

import os
import sys
from app import create_app

def main():
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found!")
        print("📝 Please copy .env.example to .env and add your API keys")
        print("💡 At minimum, you need OPENAI_API_KEY to test the app")
        return
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for at least one API key
    api_keys = [
        os.getenv('OPENAI_API_KEY'),
        os.getenv('ELEVENLABS_API_KEY'),
        os.getenv('GOOGLE_CLOUD_API_KEY'),
        os.getenv('AZURE_SPEECH_KEY')
    ]
    
    if not any(api_keys):
        print("❌ No API keys found in .env file!")
        print("🔑 Please add at least one API key to test the app")
        return
    
    # Create app
    app = create_app('development')
    
    print("🚀 Starting Quote Speak App...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    
    # Run app
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()