from dotenv import load_dotenv
import os
load_dotenv()

from authlib.integrations.flask_client import OAuth

oauth = OAuth()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate  import Migrate
from flask_login import LoginManager

db      = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

application = Flask(__name__)
application.config['SECRET_KEY'] = 'amber_pearl_latte_is_the_best'

application.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///app.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config["OAUTHLIB_INSECURE_TRANSPORT"] = True  # only for local testing

db.init_app(application)
migrate.init_app(application, db)
login_manager.init_app(application)   
oauth.init_app(application)  
google = oauth.register(
    name='google',
    api_base_url='https://www.googleapis.com/oauth2/v3/',
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    client_kwargs={'scope': 'openid email profile'},
)
login_manager.session_protection = 'strong'  # session protection level
login_manager.login_view = 'login'               # redirect anonymous users here

# ensure User model is imported so the loader can find it
from app.models import User                       

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app import routes
from app.auth import auth_bp
application.register_blueprint(auth_bp)