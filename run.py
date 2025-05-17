from app import create_app, db, login  # import the login manager from your app package
from flask_migrate import upgrade

if __name__ == "__main__":
    application = create_app()

    application.debug = True
    application.config['PROPAGATE_EXCEPTIONS'] = True

    # login is already initialized in create_app()
    login.login_view = "login"

    with application.app_context():
        upgrade()

    application.run()