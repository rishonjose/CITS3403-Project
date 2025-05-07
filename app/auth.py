import os
from flask import redirect, url_for, flash
from flask_login import login_user
from flask_dance.contrib.google import make_google_blueprint, google
from app.models import User
from app import db
from flask import Blueprint


auth_bp = Blueprint('auth', __name__)
google_bp = make_google_blueprint(
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
)

@auth_bp.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("login"))

    info = resp.json()
    email = info["email"].lower()
    username = info["name"]

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, username=username)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(f"Logged in as {username}", "success")
    return redirect(url_for("uploadpage"))