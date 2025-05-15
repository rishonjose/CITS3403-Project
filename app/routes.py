from flask import Flask, render_template, request, flash, redirect, url_for, session
from jinja2 import TemplateNotFound
from flask_wtf.csrf import CSRFProtect
from app import application, db
from app.models import BillEntry, User, SharedReport, Household
from datetime import date
from flask_login import login_user, logout_user, login_required, current_user

# Initialize CSRF protection
csrf = CSRFProtect(application)

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
@application.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").lower().strip()
        pw = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "user")
        code = request.form.get("household_code", "").strip().upper()

        if not (username and email and pw and confirm):
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if pw != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        household_id = None

        if role == "admin":
            # Generate new unique household code
            import random, string
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            while Household.query.filter_by(code=code).first():
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            new_household = Household(code=code)
            db.session.add(new_household)
            db.session.flush()  # Get ID before commit
            household_id = new_household.id
        else:
            household = Household.query.filter_by(code=code).first()
            if not household:
                flash("Invalid household code.", "error")
                return redirect(url_for("register"))
            household_id = household.id

        # Create new user
        user = User(
            username=username,
            email=email,
            role=role,
            household_code=code,
            household_id=household_id
        )
        user.set_password(pw)

        db.session.add(user)
        db.session.commit()
        login_user(user)

        session["show_household_code"] = True
        session["household_code"] = code
        return redirect(url_for("uploadpage"))

    return render_template("login-signup.html")


# Household code display
@application.route("/clear-household-code", methods=["POST"])
def clear_household_code():
    session.pop("show_household_code", None)
    session.pop("household_code", None)
    return "", 204


# LOGOUT
@application.route("/logout")
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("login"))


# PROFILE — inject household_code for admins
@application.route("/profile")
@login_required
def profile():
    # If admin, keep their household code in session
    if current_user.role == "admin":
        session["household_code"] = current_user.household_code

    # Safely build user_data, using getattr for fields that might not exist
    user_data = {
        "profile_picture_url": url_for('static', filename='images/default-avatar-icon.jpg'),
        "name":               getattr(current_user, "username", ""),
        "email":              getattr(current_user, "email", ""),
        "bio":                getattr(current_user, "bio", ""),
        "first_name":         getattr(current_user, "first_name", ""),
        "last_name":          getattr(current_user, "last_name", ""),
        "role":               getattr(current_user, "role", "")
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
        category      = request.form.get("category")
        units_str     = request.form.get("field_one", "").strip()
        cost_str      = request.form.get("field_two", "").strip()
        start_str     = request.form.get("start_date")
        end_str       = request.form.get("end_date")

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

    return render_template("uploadpage.html")


@application.route("/share", methods=["GET", "POST"])
@login_required
def share_page():
    users = User.query.filter(User.id != current_user.id).all()

    if request.method == "POST":
        selected_ids = request.form.getlist("share_to")

        if 'household' in selected_ids:
            selected_ids = [str(user.id) for user in users]

        for uid in selected_ids:
            shared = SharedReport(
                shared_by=current_user.id,
                shared_with=int(uid),
                report_url="/visualise"
            )
            db.session.add(shared)
        db.session.commit()

        flash("Report shared successfully!", "success")
        return redirect(url_for("share_page"))

    return render_template("share.html", users=users)


@application.route("/share-data", methods=["POST"])
def handle_share():
    selected = request.form.getlist("share_to")
    print("Sharing with:", selected)
    return "Shared successfully!"


@application.route("/visualise")
@application.route("/vis")
@login_required
def visualise_data():
    access = SharedReport.query.filter_by(shared_with=current_user.id).first()
    if access:
        return render_template("visualiseDataPage.html")
    else:
        flash("No report shared with you.", "error")
        return redirect(url_for("uploadpage"))


@application.route("/upload")
@application.route("/u")
def upload_data():
    return render_template("uploadpage.html")
