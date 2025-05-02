from flask import Flask, render_template, request

app = Flask(__name__)

# Homepage route
@app.route("/")
@app.route("/home")
def home():
    return render_template("landingpage.html")

# Login/signup page
@app.route("/login")
def login():
    return render_template("login-signup.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/share")
def share_page():
    # List of people and their image filenames
    users = [
        ("James", "images/avatar1.png"),
        ("Justin", "images/avatar2.png"),
        ("Sacha", "images/avatar3.png"),
        ("Rishon", "images/avatar4.png")
    ]
    return render_template("share.html", users=users)

@app.route("/share-data", methods=["POST"])
def handle_share():
    selected = request.form.getlist("share_to")
    print("Sharing with:", selected)
    return "Shared successfully!"
