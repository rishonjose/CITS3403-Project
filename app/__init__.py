import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv


load_dotenv()  # Load environment variables

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=None):
    app = Flask(__name__)

    # Use the passed config class or default to Config
    if config_class is None:
        from app.config import Config
        config_class = Config

    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY not configured! Check .env and config.py")

    # Default DB URI only if not set in config
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["OAUTHLIB_INSECURE_TRANSPORT"] = True  # Dev only

    # File upload settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    # Configure login manager
    login.login_view = 'login'
    login.session_protection = 'strong'

    # Import User model before defining user_loader
    from app.models import User

    # User loader callback for Flask-Login
    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register routes
    from app.routes import register_routes
    register_routes(app)

    return app