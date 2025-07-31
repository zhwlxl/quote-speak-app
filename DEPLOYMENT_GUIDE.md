# 🚀 Deployment Guide - Quote Speak App

## ✅ Ready to Deploy!

Your app is now organized in the `quote_speak_app_deploy/` folder with all optimizations and deployment configurations.

## 🔧 Quick Setup & Test

### 1. Install Dependencies
```bash
cd content-creation/quote_speak_app_deploy

# Install Python packages
pip install -r requirements.txt

# Install ffmpeg (macOS)
brew install ffmpeg

# Or Ubuntu/Debian
# sudo apt-get install ffmpeg
```

### 2. Configure Environment
```bash
# Copy template and edit with your API keys
cp .env.example .env
nano .env

# Add at minimum:
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Test Setup
```bash
# Run setup verification
python test_setup.py

# Should show all ✅ green checkmarks
```

### 4. Run Locally
```bash
# Start development server
python run_local.py

# Open browser to: http://localhost:5000
```

## 🌐 Production Deployment

### Option A: Railway ($5/month) - Recommended
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard:
# OPENAI_API_KEY=sk-...
# SECRET_KEY=random-secret-key
# FLASK_ENV=production
```

### Option B: Render (Free tier available)
1. Push code to GitHub
2. Connect repo to Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
5. Add environment variables in dashboard

### Option C: Docker
```bash
# Build and run
docker build -t quote-speak-app .
docker run -p 5000:5000 --env-file .env quote-speak-app
```

## 💰 Cost Breakdown

### Monthly Costs:
- **Hosting**: $5-10 (Railway/Render)
- **API Usage**: 
  - OpenAI TTS: ~$0.015/1K chars (cheapest)
  - ElevenLabs: ~$0.30/1K chars (premium)
- **Total**: $10-20/month for moderate usage

### Cost Optimization Features:
✅ Auto file cleanup (saves storage)  
✅ Optimized video compression  
✅ Smart provider defaults  
✅ Usage monitoring  
✅ Efficient resource management  

## 🔑 API Key Requirements

**Minimum (choose one):**
- OpenAI: `OPENAI_API_KEY` (recommended, cheapest)

**Optional (for more voices):**
- ElevenLabs: `ELEVENLABS_API_KEY`
- Google: `GOOGLE_CLOUD_API_KEY`
- Azure: `AZURE_SPEECH_KEY` + `AZURE_SPEECH_REGION`

## 📊 Key Improvements Made

### Code Organization:
- ✅ Modular structure (separated concerns)
- ✅ Proper error handling
- ✅ Configuration management
- ✅ Usage tracking

### Performance:
- ✅ Memory management with garbage collection
- ✅ Optimized video compression
- ✅ Automatic file cleanup
- ✅ Smart text wrapping

### Security:
- ✅ Input validation
- ✅ Secure filename generation
- ✅ Environment variable protection
- ✅ Error logging

### Deployment:
- ✅ Docker support
- ✅ Production configuration
- ✅ Health checks
- ✅ Monitoring endpoints

## 🧪 Testing Checklist

Before deploying, verify:

- [ ] `python test_setup.py` shows all ✅
- [ ] At least one API key configured
- [ ] App runs locally: `python run_local.py`
- [ ] Can generate a test video
- [ ] All font files present
- [ ] Environment variables set for production

## 🚨 Troubleshooting

**"No module named 'dotenv'"**
```bash
pip install -r requirements.txt
```

**"ffmpeg not found"**
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg
```

**"No API keys configured"**
- Edit `.env` file with actual API keys
- At minimum add `OPENAI_API_KEY`

**"Font loading error"**
- Font files should be in `static/fonts/`
- App will fallback to default fonts

## 📈 Next Steps

1. **Deploy to Railway/Render** for testing
2. **Monitor usage** via `/api/stats` endpoint
3. **Scale up** based on user feedback
4. **Add features** like user accounts, templates
5. **Optimize costs** based on actual usage patterns

## 🎯 Production Checklist

- [ ] Strong `SECRET_KEY` set
- [ ] `FLASK_ENV=production`
- [ ] API keys secured
- [ ] Monitoring enabled
- [ ] Backup strategy
- [ ] Domain configured
- [ ] SSL certificate
- [ ] Error tracking (optional)

Your app is now ready for production deployment! 🎉