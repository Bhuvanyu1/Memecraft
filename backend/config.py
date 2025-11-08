import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Settings:
    # MongoDB
    MONGO_URL = os.environ['MONGO_URL']
    DB_NAME = os.environ['DB_NAME']
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # JWT
    JWT_SECRET = os.environ.get('JWT_SECRET', 'memecraft-secret-key-change-in-production')
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # OAuth
    TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID', '')
    TWITTER_CLIENT_SECRET = os.environ.get('TWITTER_CLIENT_SECRET', '')
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', '')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET', '')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    # OpenAI (using Emergent LLM key)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'sk-emergent-8Ec72D05eBfA0C5Dd9')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://key.emergentagi.com/v1')
    
    # File Storage
    UPLOAD_DIR = ROOT_DIR / 'uploads'
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Frontend URL
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

settings = Settings()

# Create upload directory if it doesn't exist
settings.UPLOAD_DIR.mkdir(exist_ok=True)
