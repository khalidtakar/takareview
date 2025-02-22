import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/takareview' 