from flask import Flask, render_template, request, url_for, session, redirect
from flask_wtf.csrf import CSRFProtect
from jinja2 import TemplateNotFound  # Required for template error handling
from app import application

# Initialize CSRF protection
csrf = CSRFProtect(application)

# Homepage route
@application.route("/")
@application.route("/home")
def home():
    return render_template("landingpage.html")

# Login/signup page
@application.route("/login")
def login():
    return render_template("login-signup.html")

@application.route("/profile")
def profile():
    # Default user data - replace with your actual user data source
    user_data = {
        "profile_picture_url": url_for('static', filename='images/default-avatar-icon.jpg'),
        "name": "John Doe",
        "email": "john@example.com",
        "bio": "Sample user profile",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    try:
        return render_template("profile.html", user=user_data)
    except TemplateNotFound:
        return "Profile template not found", 404
    except Exception as e:
        application.logger.error(f"Error rendering profile: {str(e)}")
        return "Error loading profile page", 500

@application.route("/share")
def share_page():
    # List of people and their image filenames
    users = [
        ("James", "images/avatar1.png"),
        ("Justin", "images/avatar2.png"),
        ("Sacha", "images/avatar3.png"),
        ("Rishon", "images/avatar4.png")
    ]
    return render_template("share.html", users=users)

@application.route("/share-data", methods=["POST"])
def handle_share():
    selected = request.form.getlist("share_to")
    print("Sharing with:", selected)
    return "Shared successfully!"

@application.route("/visualise")
@application.route("/vis")
def visualise_data():
    return render_template("visualiseDataPage.html")