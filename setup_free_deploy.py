#!/usr/bin/env python3
"""
Free Deployment Setup Helper
Usage: python setup_free_deploy.py
"""

import os
import subprocess
import sys

def check_git():
    """Check if git is initialized and has remote"""
    try:
        # Check if git is initialized
        subprocess.run(['git', 'status'], capture_output=True, check=True)
        print("✅ Git repository initialized")
        
        # Check if remote exists
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Git remote configured")
            print(f"   Remote: {result.stdout.strip().split()[1]}")
            return True
        else:
            print("⚠️  No git remote configured")
            return False
    except subprocess.CalledProcessError:
        print("❌ Git not initialized")
        return False

def setup_git():
    """Help setup git repository"""
    print("\n🔧 Setting up Git repository...")
    
    if not os.path.exists('.git'):
        print("Initializing git repository...")
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Initial commit - Quote Speak App'])
    
    print("\n📝 Next steps for GitHub:")
    print("1. Go to https://github.com/new")
    print("2. Create a new repository named 'quote-speak-app'")
    print("3. Run these commands:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/quote-speak-app.git")
    print("   git push -u origin main")

def check_env():
    """Check environment configuration"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("📝 Please copy .env.example to .env and add your API keys")
        return False
    
    # Check for API keys
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'your_openai_api_key_here' in content or 'sk-' not in content:
        print("⚠️  OpenAI API key not configured in .env")
        print("🔑 Please add your actual OpenAI API key")
        return False
    
    print("✅ Environment configured")
    return True

def show_deployment_options():
    """Show deployment options"""
    print("\n🚀 Free Deployment Options:")
    print("\n1. 🥇 RENDER (Recommended - Easiest)")
    print("   • Completely free forever")
    print("   • App sleeps after 15 minutes")
    print("   • Perfect for testing")
    print("   • Guide: deploy_render.md")
    
    print("\n2. 🥈 FLY.IO (Better Performance)")
    print("   • Free tier with no sleep")
    print("   • Better performance")
    print("   • Slightly more complex")
    print("   • Guide: deploy_fly.md")
    
    print("\n3. 🥉 RAILWAY (Premium Trial)")
    print("   • $5 free credit (~1 month)")
    print("   • Best performance")
    print("   • Then $5/month")
    
    print("\n📖 Read deploy_free_comparison.md for detailed comparison")

def main():
    print("🆓 Free Deployment Setup Helper")
    print("=" * 40)
    
    # Check current directory
    if not os.path.exists('app.py'):
        print("❌ Please run this from the quote_speak_app_deploy directory")
        return
    
    print("✅ In correct directory")
    
    # Check environment
    env_ok = check_env()
    
    # Check git
    git_ok = check_git()
    
    if not git_ok:
        setup_git()
    
    if not env_ok:
        print("\n⚠️  Please configure your .env file first:")
        print("1. cp .env.example .env")
        print("2. Edit .env with your OpenAI API key")
        print("3. Run this script again")
        return
    
    # Show options
    show_deployment_options()
    
    print("\n🎯 Recommended Next Steps:")
    print("1. Push your code to GitHub (if not done)")
    print("2. Follow deploy_render.md for easiest deployment")
    print("3. Your app will be live in 5-10 minutes!")
    
    print("\n💰 Expected Costs:")
    print("• Hosting: $0 (free tier)")
    print("• API calls: $2-10/month (depending on usage)")
    print("• Total: $2-10/month")

if __name__ == '__main__':
    main()