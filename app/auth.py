import os
from flask import Blueprint, redirect, url_for, flash, current_app
from authlib.integrations.flask_client import OAuth
from flask_login import login_user
from app.models import User
from app import db

# Create a blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

from app import oauth
google = oauth.create_client('google')

@auth_bp.route("/login/google")
def google_login():
    redirect_uri = url_for('auth.google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route("/login/google/authorized")
def google_auth():
    """Handle Google OAuth callback"""
    try:
        token = google.authorize_access_token()
        if not token: # Check if token is valid
            flash("Invalid token from Google", "error")
            return redirect(url_for("login"))
        user_info = google.parse_id_token(token)
        
        email = user_info['email'].lower()
        username = user_info.get('name', email.split('@')[0])  # Fallback if no name

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, username=username, profile_pic=user_info.get('picture'))
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash(f"Logged in as {username}", "success")
        return redirect(url_for("uploadpage"))
    
    except Exception as e: # Added error handling for exceptions that might happen during Google auth
        # Log the error and redirect to login page with an error message
        flash("Failed to log in with Google", "error")
        current_app.logger.error(f"Google auth failed: {str(e)}")
        return redirect(url_for("login"))
