from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/share")
def share_page():
    # List of people and their image filenames
    users = [
        ("James", "images/avatar1.png"),
        ("Justin", "images/avatar2.png"),
        ("Sacha", "images/avatar3.png"),
        ("Rishon", "images/avatar4.png")
    ]
    
    return render_template("share.html", users=users, share_to=selected)
