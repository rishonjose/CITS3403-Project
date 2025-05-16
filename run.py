from app import application
from flask_migrate import upgrade
from flask_login import LoginManager

login_manager = LoginManager()

if __name__ == "__main__":
    application.debug = True
    application.config['PROPAGATE_EXCEPTIONS'] = True

    with application.app_context():
        upgrade()

    login_manager.login_view = "login"
    application.run()

