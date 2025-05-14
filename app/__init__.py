from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from app.config import Config
import os

load_dotenv() # Load environment variables
application = Flask(__name__) # Create application instance and apply configuration

application.config.from_object(Config)
if not application.config.get('SECRET_KEY'):
    raise ValueError("SECRET_KEY not configured! Check .env and config.py")

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect(application)

# Configure login manager
login.login_view = 'login'
login.session_protection = 'strong'

# Configure database
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config["OAUTHLIB_INSECURE_TRANSPORT"] = True  # Dev only

# Initialize extensions with app
db.init_app(application)
migrate.init_app(application, db)
login.init_app(application)


# Import routes and models AFTER initializations
from app import routes, models


# User loader callback
@login.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))