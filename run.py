# run.py
from app import application
from flask_migrate import upgrade

if __name__ == "__main__":
    # Run the Flask application
    application.run(debug=True)