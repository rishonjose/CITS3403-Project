import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db, migrate, login, csrf

load_dotenv()  # Load environment variables

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Use passed config or fallback
    if config_class is None:
        from app.config import Config
        config_class = Config

    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY not configured! Check .env and config.py")

    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["OAUTHLIB_INSECURE_TRANSPORT"] = True  # Dev only

    # File upload settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    login.login_view = 'login'
    login.session_protection = 'strong'

    # Import models here to avoid circular import
    from app.models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register routes after extensions are ready
    from app.routes import google_bp, register_routes
    app.register_blueprint(google_bp, url_prefix="/login/google")
    register_routes(app)

    return app