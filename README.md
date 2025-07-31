# Quote Speak App - Deployment Ready

A Flask web application that generates videos from text using various text-to-speech providers and custom visual styling.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (at minimum OPENAI_API_KEY)
nano .env
```

### 2. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install system dependencies (macOS)
brew install ffmpeg
```

### 3. Test Setup
```bash
# Run setup test
python test_setup.py
```

### 4. Run Locally
```bash
# Start development server
python run_local.py
```

Visit: http://localhost:5000

## 📦 Deployment Options

### Option A: Railway (Recommended - $5/month)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
```

### Option B: Render
1. Connect your GitHub repo to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. Add environment variables

### Option C: Docker
```bash
# Build image
docker build -t quote-speak-app .

# Run container
docker run -p 5000:5000 --env-file .env quote-speak-app
```

## 🔑 API Keys Required

**Minimum (Choose one):**
- `OPENAI_API_KEY` - OpenAI TTS (Recommended, cheapest)

**Optional (for more voice options):**
- `ELEVENLABS_API_KEY` - ElevenLabs (Premium quality)
- `GOOGLE_CLOUD_API_KEY` - Google Cloud TTS
- `AZURE_SPEECH_KEY` + `AZURE_SPEECH_REGION` - Azure Speech

## 🎨 Features

- **Multiple Voice Providers**: OpenAI, ElevenLabs, Google, Azure
- **Visual Customization**: 5 color templates, multiple fonts
- **Smart Text Wrapping**: Automatic text layout
- **File Management**: Auto-cleanup of old files
- **Usage Tracking**: Monitor app performance
- **Responsive UI**: Works on desktop and mobile

## 📁 Project Structure

```
quote_speak_app_deploy/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── voice_providers.py    # TTS provider implementations
├── video_generator.py    # Video creation logic
├── utils.py              # Utility functions
├── monitoring.py         # Usage tracking
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── run_local.py         # Local development runner
├── test_setup.py        # Setup verification
├── templates/
│   └── index.html       # Web interface
└── static/
    ├── fonts/          # Font files
    └── outputs/        # Generated videos
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...

# Optional
ELEVENLABS_API_KEY=...
GOOGLE_CLOUD_API_KEY=...
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=eastus

# Limits
MAX_TEXT_LENGTH=2000
MAX_TITLE_LENGTH=100
```

### Production Settings
- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY`
- Configure proper logging
- Set up monitoring

## 💰 Cost Optimization

### API Costs (per 1000 characters):
- OpenAI TTS: ~$0.015 (cheapest)
- ElevenLabs: ~$0.30 (premium)
- Google TTS: ~$0.016
- Azure: ~$0.016

### Hosting Costs:
- Railway/Render: $5-10/month
- DigitalOcean: $5-12/month
- AWS/GCP: $10-20/month (optimized)

### Cost Reduction Features:
- Auto file cleanup (saves storage)
- Optimized video compression
- Smart provider defaults
- Usage monitoring

## 🛠️ Troubleshooting

### Common Issues:

**"No API keys configured"**
- Copy `.env.example` to `.env`
- Add at least `OPENAI_API_KEY`

**"ffmpeg not found"**
- Install: `brew install ffmpeg` (macOS)
- Install: `apt-get install ffmpeg` (Ubuntu)

**"Font loading error"**
- Font files should be in `static/fonts/`
- App will fallback to default fonts

**"Video generation failed"**
- Check API key validity
- Verify text length limits
- Check disk space

### Debug Mode:
```bash
# Enable debug logging
export FLASK_ENV=development
python run_local.py
```

## 📊 Monitoring

Access usage stats at: `/api/stats`

Returns:
```json
{
  "requests": 42,
  "errors": 1,
  "error_rate": 0.024,
  "avg_generation_time": 8.5,
  "provider_usage": {
    "openai": 35,
    "elevenlabs": 7
  }
}
```

## 🔒 Security

- Input validation and sanitization
- File cleanup prevents disk filling
- Rate limiting ready (add Redis)
- Secure filename generation
- Environment variable protection

## 📈 Scaling

For higher traffic:
1. Add Redis for caching
2. Use background task queue (Celery)
3. Implement rate limiting
4. Add CDN for static files
5. Use managed database for tracking

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with `python test_setup.py`
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details