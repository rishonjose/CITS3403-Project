from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/share", methods=["GET", "POST"])
def share_page():
    users = [
        ("James", "images/avatar1.png"),
        ("Justin", "images/avatar2.png"),
        ("Sacha", "images/avatar3.png"),
        ("Rishon", "images/avatar4.png")
    ]

    shared_to = []
    if request.method == "POST":
        shared_to = request.form.getlist("share_to")
        print("✅ Shared with:", shared_to)

    return render_template("share.html", users=users, shared_to=shared_to)
