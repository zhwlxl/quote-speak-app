#!/bin/bash

# Quote Speak App Deployment Script

echo "🚀 Quote Speak App Deployment"
echo "=============================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.example to .env and add your API keys"
    exit 1
fi

# Check for API keys
if ! grep -q "sk-" .env && ! grep -q "your_.*_api_key_here" .env; then
    echo "⚠️  No API keys found in .env file"
    echo "🔑 Please add at least OPENAI_API_KEY to test the app"
fi

echo "1. Installing dependencies..."
pip install -r requirements.txt

echo "2. Testing setup..."
python test_setup.py

echo "3. Creating directories..."
mkdir -p static/outputs static/fonts

echo "4. Setting permissions..."
chmod +x run_local.py test_setup.py

echo "✅ Deployment ready!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to .env file"
echo "2. Run: python run_local.py"
echo "3. Open: http://localhost:5000"
echo ""
echo "For production deployment:"
echo "- Railway: railway up"
echo "- Render: Connect GitHub repo"
echo "- Docker: docker build -t quote-speak-app ."