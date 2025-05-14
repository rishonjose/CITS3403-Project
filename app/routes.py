import os
from werkzeug.utils import secure_filename
from app.utils import parse_pdf_bill
from flask import (
    render_template, request, flash,
    redirect, url_for, jsonify, abort
)
from collections import defaultdict
from jinja2 import TemplateNotFound
from flask_wtf.csrf import CSRFProtect
from datetime import date, datetime
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)

from app import application, db
from app.models import BillEntry, User

# Initialize CSRF protection
csrf = CSRFProtect(application)

ALLOWED_EXT = {'pdf'}
def allowed(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT
    )


@application.route("/")
@application.route("/home")
def home():
    return render_template("landingpage.html")


# ─── AUTH ──────────────────────────────────────────────────────────────────────

@application.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        pw    = request.form.get("password", "")
        user  = User.query.filter_by(email=email).first()
        if user and user.check_password(pw):
            login_user(user)
            return redirect(url_for("uploadpage"))
        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))
    return render_template("login-signup.html")


@application.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").lower().strip()
        pw       = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

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


@application.route("/logout")
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("login"))


# ─── PROFILE ───────────────────────────────────────────────────────────────────

@application.route("/profile")
@login_required
def profile():
    # Placeholder; swap in your real user lookup
    user_data = {
        "profile_picture_url": url_for(
            'static',
            filename='images/default-avatar-icon.jpg'
        ),
        "name": current_user.username,
        "email": current_user.email,
        "bio": "",
        "first_name": "",
        "last_name": ""
    }

    try:
        return render_template("profile.html", user=user_data)
    except TemplateNotFound:
        return "Profile template not found", 404
    except Exception as e:
        application.logger.error(f"Error rendering profile: {e}")
        return "Error loading profile page", 500


# ─── UPLOAD PAGE ────────────────────────────────────────────────────────────────

@application.route("/upload", methods=["GET", "POST"])
@login_required
def uploadpage():
    if request.method == "POST":
        # —— PDF Upload & Parse ——
        pdf = request.files.get("pdf_file")
        if pdf and allowed(pdf.filename):
            filename = secure_filename(pdf.filename)
            upload_dir = application.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            pdf.save(save_path)

            try:
                data = parse_pdf_bill(save_path)
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
                flash(
                    "Couldn’t parse the PDF completely. "
                    "Please enter manually.",
                    "error"
                )
                # fall through to manual-entry

        # —— Manual Entry ——
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
            flash(
                "Units, cost, and dates must be valid.",
                "error"
            )
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

    # GET → render form
    return render_template("uploadpage.html")


# ─── SHARE PAGE ────────────────────────────────────────────────────────────────

@application.route("/share")
@login_required
def share_page():
    users = [
        ("James", "images/avatar1.png"),
        ("Justin", "images/avatar2.png"),
        ("Sacha", "images/avatar3.png"),
        ("Rishon", "images/avatar4.png")
    ]
    return render_template("share.html", users=users)


@application.route("/share-data", methods=["POST"])
@login_required
def handle_share():
    selected = request.form.getlist("share_to")
    # process sharing…
    flash(f"Shared with: {', '.join(selected)}", "success")
    return redirect(url_for("share_page"))


# ─── VISUALISATION & API ───────────────────────────────────────────────────────

@application.route("/visualise")
@application.route("/vis")
@login_required
def visualise_data():
    recent = (
        BillEntry.query
        .filter_by(user_id=current_user.id)
        .order_by(BillEntry.created_at.desc())
        .limit(4)
        .all()
    )
    return render_template("visualiseDataPage.html", recent_bills=recent)


@application.route('/api/analytics')
@login_required
def analytics_api():
    raw = defaultdict(lambda: defaultdict(float))
    entries = BillEntry.query.filter_by(
        user_id=current_user.id
    ).all()

    for e in entries:
        mon = e.start_date.strftime('%b %Y')
        raw[mon][e.category] += e.units * e.cost_per_unit

    # sort months chronologically
    months = sorted(
        raw.keys(),
        key=lambda m: datetime.strptime(m, '%b %Y')
    )

    utils     = ['Electricity','Water','Gas','WiFi','Other']
    totalBill = [ sum(raw[m].values()) for m in months ]
    util_data = {
        u: [ raw[m].get(u, 0) for m in months ]
        for u in utils
    }
    colours = ['orange','blue','green','violet','grey']

    return jsonify({
        'month_labels': months,
        'util_labels' : utils,
        'util_colours': colours,
        'totalBill'   : totalBill,
        'util_data'   : util_data
    })


@application.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = BillEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash("That’s not your bill to delete!", "error")
        return redirect(url_for('visualise_data'))

    db.session.delete(entry)
    db.session.commit()
    flash("Bill deleted.", "success")
    return redirect(url_for('visualise_data'))


@application.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = BillEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash("Cannot edit someone else’s bill.", "error")
        return redirect(url_for('visualise_data'))

    if request.method == 'POST':
        # pull & validate exactly like uploadpage()
        try:
            entry.category      = request.form['category']
            entry.units         = float(request.form['field_one'])
            entry.cost_per_unit = float(request.form['field_two'])
            entry.start_date    = date.fromisoformat(request.form['start_date'])
            entry.end_date      = date.fromisoformat(request.form['end_date'])
        except (ValueError, TypeError):
            flash("Invalid data; please try again.", "error")
            return redirect(url_for('edit_entry', entry_id=entry_id))

        db.session.commit()
        flash("Bill updated!", "success")
        return redirect(url_for('visualise_data'))

    # GET → pre-populate a simple edit form
    return render_template('edit_bill.html', bill=entry)




@application.route("/u")
@login_required
def upload_data():
    return render_template("uploadpage.html")
