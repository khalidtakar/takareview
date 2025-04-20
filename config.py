import os
from dotenv import load_dotenv

load_dotenv()

# Get the API key at module level
GOOGLE_API_KEY = os.environ.get('GEMINI_API_KEY')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://kdfwyuhzeynzrnfldwyl.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # Make sure this is set in your .env file
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')  # Add your Gemini API key to .env file
    
    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # OAuth Configuration
    SITE_URL = 'https://kdfwyuhzeynzrnfldwyl.supabase.co'
    OAUTH_REDIRECT_URI = 'http://127.0.0.1:5000/auth/callback'  # Local development URL
    OAUTH_PROVIDERS = {
        'google': {
            'redirect_uri': 'http://127.0.0.1:5000/auth/callback'
        },
        'twitter': {
            'client_id': os.getenv('TWITTER_CLIENT_ID'),
            'client_secret': os.getenv('TWITTER_CLIENT_SECRET'),
            'redirect_uri': 'http://127.0.0.1:5000/auth/callback',
            'site_url': 'https://kdfwyuhzeynzrnfldwyl.supabase.co'
        }
    }
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Get Database URL from environment variable
    database_url = DATABASE_URL
    
    # If the URL starts with postgres://, replace it with postgresql://
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = SECRET_KEY 