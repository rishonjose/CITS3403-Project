from dotenv import load_dotenv
import os
load_dotenv()

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
login_manager.login_view = 'login'               # redirect anonymous users here

# ensure User model is imported so the loader can find it
from app.models import User                       

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app import routes
from app.auth import auth_bp, google_bp
application.register_blueprint(google_bp, url_prefix="/login")
application.register_blueprint(auth_bp)