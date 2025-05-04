from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate  import Migrate

db      = SQLAlchemy()
migrate = Migrate()

application = Flask(__name__)
application.config['SECRET_KEY'] = 'amber_pearl_latte_is_the_best'

application.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///app.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(application)
migrate.init_app(application, db)

from app import routes