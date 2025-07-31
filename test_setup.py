#!/usr/bin/env python3
"""
Test setup and dependencies
Usage: python test_setup.py
"""

import os
import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'pillow', 'moviepy', 'openai', 
        'requests', 'python-dotenv', 'gunicorn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return missing

def check_system_dependencies():
    """Check system dependencies"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
        print("✅ ffmpeg")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg (required for video generation)")
        print("💡 Install with: brew install ffmpeg (macOS)")
        return False
    return True

def check_env_file():
    """Check .env file"""
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
            'GOOGLE_CLOUD_API_KEY': os.getenv('GOOGLE_CLOUD_API_KEY'),
            'AZURE_SPEECH_KEY': os.getenv('AZURE_SPEECH_KEY')
        }
        
        configured = 0
        for key, value in api_keys.items():
            if value and value != 'your_api_key_here':
                print(f"✅ {key}")
                configured += 1
            else:
                print(f"⚠️  {key} (not configured)")
        
        if configured == 0:
            print("❌ No API keys configured")
            return False
        
        return True
    else:
        print("❌ .env file missing")
        print("💡 Copy .env.example to .env and add your API keys")
        return False

def check_directories():
    """Check required directories"""
    dirs = ['static/fonts', 'static/outputs', 'templates']
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created {dir_path}")

def main():
    print("🔍 Testing Quote Speak App Setup...\n")
    
    print("1. Python Version:")
    python_ok = check_python_version()
    
    print("\n2. Python Dependencies:")
    missing = check_dependencies()
    
    print("\n3. System Dependencies:")
    system_ok = check_system_dependencies()
    
    print("\n4. Environment Configuration:")
    env_ok = check_env_file()
    
    print("\n5. Directory Structure:")
    check_directories()
    
    print("\n" + "="*50)
    
    if not python_ok:
        print("❌ Setup Failed: Python version too old")
        return
    
    if missing:
        print("❌ Setup Failed: Missing dependencies")
        print(f"💡 Install with: pip install {' '.join(missing)}")
        return
    
    if not system_ok:
        print("❌ Setup Failed: Missing system dependencies")
        return
    
    if not env_ok:
        print("❌ Setup Failed: Environment not configured")
        return
    
    print("✅ Setup Complete! Ready to run the app")
    print("🚀 Run with: python run_local.py")

if __name__ == '__main__':
    main()