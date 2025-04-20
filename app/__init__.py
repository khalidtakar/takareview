from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil import parser

# Load environment variables first
load_dotenv()

from flask import Flask
from config import Config
from app.database import init_supabase
from app.extensions import login_manager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()

def timeago(value):
    """Format a date time to a human readable time ago string"""
    try:
        if isinstance(value, str):
            value = parser.parse(value)
        now = datetime.utcnow()
        diff = now - value

        if diff.days > 365:
            return f"{diff.days // 365} years ago"
        if diff.days > 30:
            return f"{diff.days // 30} months ago"
        if diff.days > 0:
            return f"{diff.days} days ago"
        if diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        if diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        return "Just now"
    except Exception:
        return value

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Import models to ensure they're known to Flask
    from app.models.user import User
    from app.models.tweet_analysis import TweetAnalysis
    
    # Initialize extensions
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    with app.app_context():
        init_supabase()

    # Import blueprints
    from app.routes import main_bp, auth_bp, analyse_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analyse_bp)

    # Add the timeago filter
    app.jinja_env.filters['timeago'] = timeago

    return app 