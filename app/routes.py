import os
from werkzeug.utils import secure_filename
from app.utils import parse_pdf_bill
from flask import Flask, render_template, request, flash, redirect, url_for
from jinja2 import TemplateNotFound
from flask_wtf.csrf import CSRFProtect
from app import application, db
from app.models import BillEntry, User
from datetime import date 
from flask_login import login_user, logout_user, login_required, current_user

# Initialize CSRF protection
csrf = CSRFProtect(application)

ALLOWED_EXT = {'pdf'}
def allowed(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

# Homepage route
@application.route("/")
@application.route("/home")
def home():
    return render_template("landingpage.html")

# Login/signup page
# LOGIN
@application.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").lower().strip()
        pw    = request.form.get("password","")
        user  = User.query.filter_by(email=email).first()
        if user and user.check_password(pw):
            login_user(user)
            return redirect(url_for("uploadpage"))
        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))
    return render_template("login-signup.html")

# REGISTER
@application.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        email    = request.form.get("email","").lower().strip()
        pw       = request.form.get("password","")
        confirm  = request.form.get("confirm_password","")
        if not (username and email and pw and confirm):
            flash("All fields are required.", "error")
            return redirect(url_for("register"))
        if pw != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(pw)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome, {username}!", "success")
        return redirect(url_for("uploadpage"))
    return render_template("login-signup.html")

# LOGOUT
@application.route("/logout")
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("login"))


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

@application.route("/upload", methods=["GET", "POST"])
@login_required
def uploadpage():
    if request.method == "POST":
        # ——— PDF Upload/Parse branch ———
        pdf = request.files.get("pdf_file")
        if pdf and allowed(pdf.filename):
            filename = secure_filename(pdf.filename)
            upload_dir = application.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            pdf.save(save_path)

            try:
                data = parse_pdf_bill(save_path)
                # convert & validate parsed values
                units      = float(data["units"])
                cost       = float(data["cost"])
                start_date = date.fromisoformat(data["start_date"])
                end_date   = date.fromisoformat(data["end_date"])

                entry = BillEntry(
                    user_id       = current_user.id,
                    category      = data.get("category", "Other"),
                    units         = units,
                    cost_per_unit = cost,
                    start_date    = start_date,
                    end_date      = end_date
                )
                db.session.add(entry)
                db.session.commit()
                flash("PDF parsed and entry saved!", "success")
                return redirect(url_for("uploadpage"))
            except Exception:
                flash("Couldn’t parse the PDF completely. Please enter manually.", "error")
                # fall‐through to manual entry

        # ——— Manual‐entry branch ———
        category   = request.form.get("category")
        units_str  = request.form.get("field_one", "").strip()
        cost_str   = request.form.get("field_two", "").strip()
        start_str  = request.form.get("start_date")
        end_str    = request.form.get("end_date")

        try:
            units      = float(units_str)
            cost       = float(cost_str)
            start_date = date.fromisoformat(start_str)
            end_date   = date.fromisoformat(end_str)
        except (ValueError, TypeError):
            flash("Units, cost, and dates must be valid.", "error")
            return redirect(url_for("uploadpage"))

        entry = BillEntry(
            user_id       = current_user.id,
            category      = category,
            units         = units,
            cost_per_unit = cost,
            start_date    = start_date,
            end_date      = end_date
        )
        db.session.add(entry)
        db.session.commit()

        flash("Bill entry saved successfully!", "success")
        return redirect(url_for("uploadpage"))

    # on GET, just render the form
    return render_template("uploadpage.html")

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

@application.route("/upload")
@application.route("/u")
def upload_data():
    return render_template("uploadpage.html")