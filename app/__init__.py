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

db.init_app(application)
migrate.init_app(application, db) 
login_manager.init_app(application)              
login_manager.login_view = 'login'

from app.models import User                       

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app import routes
