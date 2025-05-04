from flask import Flask, render_template, request
from app import application

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
    return render_template("profile.html")

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
