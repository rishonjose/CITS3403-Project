import os
from werkzeug.utils import secure_filename
from app.utils import parse_pdf_bill
from flask import (
    Flask, render_template, request, flash,
    redirect, url_for, jsonify, abort
)
from flask_dance.contrib.google import make_google_blueprint, google
from collections import defaultdict
from jinja2 import TemplateNotFound
from flask_wtf.csrf import CSRFProtect
from datetime import date, datetime
from calendar import monthrange
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from app import application, db
from app.models import BillEntry, User
from app.forms import LoginForm, RegistrationForm, BillEntryForm

google_bp = make_google_blueprint(client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"), 
                                  client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"), 
                                  redirect_to="google_login_authorized")
application.register_blueprint(google_bp, url_prefix='/google_login')

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
# Login/signup page
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
            flash("Logged in successfully!", "success")
            return redirect(next_page or url_for('uploadpage'))
        flash("Invalid email or password", "error")
    
    return render_template("login-signup.html", 
                         login_form=login_form, 
                         reg_form=RegistrationForm())

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
                profile_pic="images/default_profile.png",  # Default profile picture
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

@application.route("/logout")
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("login"))

@application.route("/profile", methods=["GET", "POST"]) # <-- GET/POST method action on button
@login_required
def profile(): # Profile user lookup now includes username
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

# ─── UPLOAD PAGE ────────────────────────────────────────────────────────────────
@application.route("/upload", methods=["GET", "POST"])
@login_required
def uploadpage():
    form = BillEntryForm()
    
    # 1) PDF branch takes precedence if they uploaded a PDF
    if form.validate_on_submit() is False and 'pdf_file' in request.files:
        pdf = request.files['pdf_file']
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
                    "Couldn't parse the PDF completely. "
                    "Please enter manually.",
                    "error"
                )
                # fall through to manual-entry


    # 2) Manual‐entry branch via WTForms
    if form.validate_on_submit():
        entry = BillEntry(
            user_id       = current_user.id,
            category      = form.category.data,
            units         = form.units.data,
            cost_per_unit = form.cost_per_unit.data,
            start_date    = form.start_date.data,
            end_date      = form.end_date.data
        )
        db.session.add(entry)
        db.session.commit()
        flash("Bill entry saved successfully!","success")
        return redirect(url_for("uploadpage"))

    # 3) on GET or on any validation errors, render the page & form
    return render_template("uploadpage.html", form=form)

# ─── SHARE PAGE ────────────────────────────────────────────────────────────────
@application.route("/share")
@login_required
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

    # figure out last two months' totals
    if len(months) >= 2:
        this_total = totalBill[-1]
        prev_total = totalBill[-2]
        pct_change = round((this_total - prev_total) / prev_total * 100, 1)
    else:
        this_total = prev_total = pct_change = None

    # days in that last month
    last_mon_str = months[-1]                  # e.g. "May 2025"
    dt = datetime.strptime(last_mon_str, '%b %Y')
    days = monthrange(dt.year, dt.month)[1]   # 31, 30, etc.

    avg_per_day = round(this_total / days, 2) if this_total else None
    
    return jsonify({
        'month_labels': months,
        'util_labels' : utils,
        'util_colours': colours,
        'totalBill'   : totalBill,
        'util_data'   : util_data,
        'this_month_total': this_total,
        'pct_change'  : pct_change,
        'avg_per_day' : avg_per_day,
    })


@application.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = BillEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash("That's not your bill to delete!", "error")
        return redirect(request.referrer or url_for('visualise_data'))

    db.session.delete(entry)
    db.session.commit()
    flash("Bill deleted.", "success")
    return redirect(request.referrer or url_for('visualise_data'))


@application.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = BillEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash("Cannot edit someone else's bill.", "error")
        return redirect(request.referrer or url_for('visualise_data'))

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
            return redirect(request.referrer or url_for('visualise_data'))

        db.session.commit()
        flash("Bill updated!", "success")
        return redirect(request.referrer or url_for('visualise_data'))

    # GET → pre-populate a simple edit form
    return render_template('edit_bill.html', bill=entry)


@application.route('/history')
@login_required
def bill_history():
    page = request.args.get('page', 1, type=int)
    pagination = (BillEntry.query
                  .filter_by(user_id=current_user.id)
                  .order_by(BillEntry.created_at.desc())
                  .paginate(page=page, per_page=20))
    return render_template(
      'history.html',
      bills=pagination.items,
      prev_page=pagination.prev_num,
      next_page=pagination.next_num
    )


@application.route("/u")
@login_required
def upload_data():
    return render_template("uploadpage.html")