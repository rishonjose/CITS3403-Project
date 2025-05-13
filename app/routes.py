from flask import Flask, render_template, request, flash, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user # login_user, logout_user is used for session management (implemented or not double check)
from flask_dance.contrib.google import make_google_blueprint
from app import application, db
from app.models import BillEntry, User
from datetime import date 
from app.forms import LoginForm, RegistrationForm, BillEntryForm

google_bp = make_google_blueprint(client_id="YOUR_GOOGLE_CLIENT_ID", 
                                  client_secret="YOUR_GOOGLE_CLIENT_SECRET", 
                                  redirect_to="google_login_authorized")
application.register_blueprint(google_bp, url_prefix='/google_login')

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
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page or url_for('uploadpage'))
        flash("Invalid email or password", "error")
    
    return render_template("login-signup.html", form=form)

@application.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('uploadpage'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data.lower(),
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Account created for {form.username.data}!", "success")
            return redirect(url_for('uploadpage'))
        except Exception as e:
            db.session.rollback()
            application.logger.error(f"Registration failed: {str(e)}")
            flash("Registration failed. Please try again.", "error")
    return render_template("login-signup.html", form=form)


def get_or_create_user(user_data):
    """ Function to check if the user exists in the database, otherwise create a new user. """
    user = User.query.filter_by(email=user_data['emails'][0]['value']).first()
    if not user:
        user = User(email=user_data['emails'][0]['value'], name=user_data['displayName'])
        db.session.add(user)
        db.session.commit()
    return user

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