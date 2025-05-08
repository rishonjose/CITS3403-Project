# run.py
from app import application
from flask_migrate import upgrade

if __name__ == "__main__":

    # ensure migrations are applied before the first request
    with application.app_context():
        # this will create the migrations folder if missing,
        # and then run all unapplied migrations
        upgrade()
    application.run(debug=True)

