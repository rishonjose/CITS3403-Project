from app import application
from flask_migrate import upgrade

if __name__ == "__main__":
    # Ensure migrations are applied before the first request
    with application.app_context():
        # This will create the migrations folder if missing, and then run all unapplied migrations
        upgrade()
    
    # Run the application
    application.run(debug=True)
