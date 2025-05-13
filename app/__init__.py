from dotenv import load_dotenv
import os
load_dotenv()

from authlib.integrations.flask_client import OAuth

oauth = OAuth()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate  import Migrate
from flask_login import LoginManager

class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY")

application = Flask(__name__)
application.config.from_object(Config)

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base, session_options={"autoflush": False})

migrate = Migrate()
login = LoginManager()
login.login_view = 'login'             # login view function
login.session_protection = 'strong'     # session protection level

application.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///app.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config["OAUTHLIB_INSECURE_TRANSPORT"] = True  # only for local testing

db.init_app(application)
migrate.init_app(application, db)
login.init_app(application)   
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

# ensure User model is imported so the loader can find it
from app.models import User                       


from app import routes
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(application)

from app.auth import auth_bp
application.register_blueprint(auth_bp)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # This function loads the user from the session

from app import forms