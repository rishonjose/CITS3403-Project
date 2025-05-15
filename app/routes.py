import os
from flask import Flask, render_template, request, flash, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user # login_user, logout_user is used for session management (implemented or not double check)
from flask_dance.contrib.google import make_google_blueprint, google
from app import application, db
from app.models import BillEntry, User
from datetime import date 
from app.forms import LoginForm, RegistrationForm, BillEntryForm

google_bp = make_google_blueprint(client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"), 
                                  client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"), 
                                  redirect_to="google_login_authorized")
application.register_blueprint(google_bp, url_prefix='/google_login')



# Initialize CSRF protection
csrf = CSRFProtect(application)

# Homepage route
@application.route("/")
@application.route("/home")
def home():
    return render_template("landingpage.html")

# Login/signup page
# LOGIN
@application.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('uploadpage'))
    
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data.lower()).first()
        if user and user.check_password(login_form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f"Logged in successfully!", "success")
            return redirect(next_page or url_for('uploadpage'))
        flash("Invalid email or password", "error")
    
    return render_template("login-signup.html", login_form=login_form, reg_form=RegistrationForm())

@application.route("/register", methods=["GET", "POST"])
def register():
    reg_form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('uploadpage'))
    
    if reg_form.validate_on_submit():
        try:
            user = User(
                username=reg_form.username.data,
                email=reg_form.email.data.lower(),
            )
            user.set_password(reg_form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Account created for {reg_form.username.data}!", "success")
            return redirect(url_for('uploadpage'))
        except Exception as e:
            db.session.rollback()
            application.logger.error(f"Registration failed: {str(e)}")
            flash("Registration failed. Please try again.", "error")
    return render_template("login-signup.html", login_form=LoginForm(), reg_form=reg_form)

def get_or_create_user(user_data):
    """ Function to check if the user exists in the database, otherwise create a new user. """
    user = User.query.filter_by(email=user_data['emails'][0]['value']).first()
    if not user:
        user = User(email=user_data['emails'][0]['value'], name=user_data['displayName'])
        db.session.add(user)
        db.session.commit()
    return user

@application.route("/google_login/authorized")
def google_login_authorized():
    """Handle Google OAuth callback with full error handling"""
    try:
        # Check if OAuth succeeded
        if not google.authorized:
            flash("Access denied by Google or session expired.", "error")
            return redirect(url_for("login"))

        # Fetch and validate token
        token = google.access_token
        if not token:
            flash("Invalid token from Google", "error")
            return redirect(url_for("login"))

        # Get user info (with error handling for API failures)
        try:
            resp = google.get("/oauth2/v2/userinfo")
            if not resp.ok:
                flash("Failed to fetch user data from Google", "error")
                return redirect(url_for("login"))
            user_info = resp.json()
        except Exception as e:
            application.logger.error(f"Google API error: {str(e)}")
            flash("Google service temporarily unavailable", "error")
            return redirect(url_for("login"))

        # Extract and normalize user data
        email = user_info["email"].lower()
        username = user_info.get("name", email.split("@")[0])
        profile_pic = user_info.get("picture")

        # Database operations (with transaction safety)
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    username=username,
                    profile_pic=profile_pic,
                    is_oauth_user=True  # Optional: flag for OAuth users
                )
                db.session.add(user)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            application.logger.error(f"Database error: {str(e)}")
            flash("Account creation failed", "error")
            return redirect(url_for("login"))

        # Finalize login
        login_user(user)
        flash(f"Welcome, {username}!", "success")
        return redirect(url_for("uploadpage"))

    # Catch-all for unexpected errors
    except Exception as e:
        application.logger.critical(f"Unexpected auth error: {str(e)}")
        flash("Login failed due to system error", "error")
        return redirect(url_for("login"))
    
# LOGOUT
@application.route("/logout")
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("login"))

# New profile route logic, including usernames
@application.route("/profile", methods=["GET", "POST"]) # <-- GET/POST method action on button
@login_required
def profile():
    if request.method == "POST":
        new_username = request.form.get("username").strip()
        if new_username:
            if new_username != current_user.username:
                existing = User.query.filter_by(username=new_username).first()
                if existing:
                    flash("Username already taken.", "error")
                else:
                    current_user.username = new_username
                    db.session.commit()
                    flash("Username updated successfully!", "success")
            else:
                flash("That's already your current username.", "info")
        else:
            flash("Username cannot be empty.", "error")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=current_user)

@application.route("/upload", methods=["GET", "POST"])
@login_required
def uploadpage():
    form = BillEntryForm()
    if form.validate_on_submit():
        try:
            entry = BillEntry(
                user_id=current_user.id,
                category=form.category.data,
                units=form.units.data,
                cost_per_unit=form.cost_per_unit.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data
            )
            db.session.add(entry)
            db.session.commit()
            flash("Bill entry saved successfully!", "success")
            return redirect(url_for('visualisedatapage'))  # Redirect to visualiseData / 'analytics' page
        except Exception as e:
            db.session.rollback()
            application.logger.error(f"Bill entry failed: {str(e)}")
            flash("Failed to save bill. Please try again.", "error")
    
    return render_template("uploadpage.html", form=form)

@application.route("/share")
def share_page():
    # List of people and their image filenames (from user.profile_pic) + TODO: should be real users added not dummy
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

@application.route("/analytics")
@login_required
def visualisedatapage():
    # Get user's bill entries
    entries = BillEntry.query.filter_by(user_id=current_user.id).all()
    return render_template("visualisedatapage.html", entries=entries)