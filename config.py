import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'outputs')
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
    GOOGLE_CLOUD_API_KEY = os.environ.get('GOOGLE_CLOUD_API_KEY')
    AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
    AZURE_SPEECH_REGION = os.environ.get('AZURE_SPEECH_REGION', 'eastus')
    
    # Redis for caching (optional)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    
    # Text limits
    MAX_TEXT_LENGTH = int(os.environ.get('MAX_TEXT_LENGTH', 2000))
    MAX_TITLE_LENGTH = int(os.environ.get('MAX_TITLE_LENGTH', 100))

class ProductionConfig(Config):
    DEBUG = False
    
class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}