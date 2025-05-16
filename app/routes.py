import os
import random
import string
from datetime import date, datetime

from flask import (
    render_template, request, flash,
    redirect, url_for, session, jsonify
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from flask_dance.contrib.google import make_google_blueprint
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import BillEntry, User, SharedReport, Household
from app.forms import LoginForm, RegistrationForm, BillEntryForm
from app.utils import parse_pdf_bill

# Google OAuth blueprint
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    redirect_to="google_login_authorized"
)

ALLOWED_EXT = {'pdf'}
def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def home():
    return render_template("landingpage.html")

def register_blueprints(app):
    app.register_blueprint(google_bp, url_prefix='/google_login')

def register_routes(app):
    csrf = CSRFProtect(app)
    def home():
        return render_template("landingpage.html")
    app.add_url_rule("/", 'home', home)
    app.add_url_rule("/home", 'home_alt', home)

    # ——— AUTHENTICATION ———
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("uploadpage"))

        login_form = LoginForm()
        reg_form = RegistrationForm()

        if login_form.validate_on_submit():
            email = login_form.email.data.lower().strip()
            pw = login_form.password.data
            user = User.query.filter_by(email=email).first()

            if user and user.check_password(pw):
                login_user(user)
                flash("Logged in successfully!", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("uploadpage"))
            flash("Invalid email or password", "error")

        return render_template(
            "login-signup.html",
            login_form=login_form,
            reg_form=reg_form
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("uploadpage"))

        reg_form = RegistrationForm()
        if reg_form.validate_on_submit():
            username = reg_form.username.data.strip()
            email = reg_form.email.data.lower().strip()
            pw = reg_form.password.data
            confirm = reg_form.confirm_password.data
            role = reg_form.role.data or "user"
            code = (reg_form.household_code.data or "").strip().upper()

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
                # Generate unique household code
                while True:
                    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not Household.query.filter_by(code=code).first():
                        break
                new_hh = Household(code=code)
                db.session.add(new_hh)
                db.session.flush()
                household_id = new_hh.id
            else:
                household = Household.query.filter_by(code=code).first()
                if not household:
                    flash("Invalid household code.", "error")
                    return redirect(url_for("register"))
                household_id = household.id

            try:
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
                flash(f"Account created for {username}!", "success")
                return redirect(url_for("uploadpage"))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Registration failed: {e}")
                flash("Registration failed. Please try again.", "error")
                return redirect(url_for("register"))

        return render_template(
            "login-signup.html",
            login_form=LoginForm(),
            reg_form=reg_form
        )

    @app.route("/google_login/authorized")
    def google_login_authorized():
        try:
            if not google.authorized:
                flash("Access denied by Google or session expired.", "error")
                return redirect(url_for("login"))

            resp = google.get("/oauth2/v2/userinfo")
            if not resp.ok:
                flash("Failed to fetch user data from Google", "error")
                return redirect(url_for("login"))
            info = resp.json()

            email = info["email"].lower()
            username = info.get("name", email.split("@")[0])
            profile_pic = info.get("picture")

            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    username=username,
                    email=email,
                    profile_pic=profile_pic,
                    is_oauth_user=True
                )
                db.session.add(user)
                db.session.commit()

            login_user(user)
            flash("Logged in with Google!", "success")
            return redirect(url_for("uploadpage"))
        except Exception as e:
            app.logger.error(f"Google login error: {e}")
            flash("Google login failed.", "error")
            return redirect(url_for("login"))

    @app.route("/logout")
    def logout():
        logout_user()
        flash("You've been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/clear-household-code", methods=["POST"])
    def clear_household_code():
        session.pop("show_household_code", None)
        session.pop("household_code", None)
        return "", 204

    # ——— PROFILE ———
    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        if request.method == "POST":
            new_username = request.form.get("username", "").strip()
            if new_username:
                if new_username != current_user.username:
                    if User.query.filter_by(username=new_username).first():
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

        if current_user.role == "admin":
            session["household_code"] = current_user.household_code

        user_data = {
            "profile_picture_url": url_for('static', filename='images/default-avatar-icon.jpg'),
            "name": current_user.username,
            "email": current_user.email,
            "bio": getattr(current_user, "bio", ""),
            "first_name": getattr(current_user, "first_name", ""),
            "last_name": getattr(current_user, "last_name", ""),
            "role": current_user.role
        }
        try:
            return render_template("profile.html", user=user_data)
        except TemplateNotFound:
            return "Profile template not found", 404
        except Exception as e:
            app.logger.error(f"Error rendering profile: {e}")
            return "Error loading profile page", 500

    # ——— UPLOAD & BILL ENTRY ———
    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def uploadpage():
        form = BillEntryForm()

        # PDF upload
        if 'pdf_file' in request.files and request.files['pdf_file'].filename:
            pdf = request.files['pdf_file']
            if pdf and allowed(pdf.filename):
                filename = secure_filename(pdf.filename)
                upload_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, filename)
                pdf.save(save_path)
                try:
                    data = parse_pdf_bill(save_path)
                    entry = BillEntry(
                        user_id=current_user.id,
                        category=data.get('category', 'Other'),
                        units=float(data['units']),
                        cost_per_unit=float(data['cost']),
                        start_date=date.fromisoformat(data['start_date']),
                        end_date=date.fromisoformat(data['end_date'])
                    )
                    db.session.add(entry)
                    db.session.commit()
                    flash("PDF parsed and entry saved!", "success")
                    return redirect(url_for("uploadpage"))
                except Exception:
                    flash("Couldn't parse the PDF completely. Please enter manually.", "error")

        # Manual entry
        if form.validate_on_submit():
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
            return redirect(url_for("uploadpage"))

        return render_template("uploadpage.html", form=form)

    # ——— SHARING ———
    @app.route("/share", methods=["GET", "POST"])
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

    @app.route("/share-data", methods=["POST"])
    @login_required
    def handle_share():
        selected = request.form.getlist("share_to")
        flash(f"Shared with: {', '.join(selected)}", "success")
        return redirect(url_for("share_page"))

    # ——— VISUALISATION & API ———
    @app.route("/visualise")
    @app.route("/vis")
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

    @app.route('/api/analytics')
    @login_required
    def analytics_api():
        raw = defaultdict(lambda: defaultdict(float))
        entries = BillEntry.query.filter_by(user_id=current_user.id).all()
        for e in entries:
            mon = e.start_date.strftime('%b %Y')
            raw[mon][e.category] += e.units * e.cost_per_unit

        months = sorted(raw.keys(), key=lambda m: datetime.strptime(m, '%b %Y'))
        utils = ['Electricity','Water','Gas','WiFi','Other']
        totalBill = [ sum(raw[m].values()) for m in months ]
        util_data = { u: [ raw[m].get(u, 0) for m in months ] for u in utils }
        colours = ['orange','blue','green','violet','grey']

        if len(months) >= 2:
            this_total = totalBill[-1]
            prev_total = totalBill[-2]
            pct_change = round((this_total - prev_total) / prev_total * 100, 1)
        else:
            this_total = prev_total = pct_change = None

        last_mon_str = months[-1] if months else None
        days = monthrange(datetime.strptime(last_mon_str, '%b %Y').year, datetime.strptime(last_mon_str, '%b %Y').month)[1] if last_mon_str else None
        avg_per_day = round(this_total / days, 2) if this_total and days else None

        return jsonify({
            'month_labels': months,
            'util_labels': utils,
            'util_colours': colours,
            'totalBill': totalBill,
            'util_data': util_data,
            'this_month_total': this_total,
            'pct_change': pct_change,
            'avg_per_day': avg_per_day,
        })

    @app.route('/entry/<int:entry_id>/delete', methods=['POST'])
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

    @app.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_entry(entry_id):
        entry = BillEntry.query.get_or_404(entry_id)
        if entry.user_id != current_user.id:
            flash("Cannot edit someone else's bill.", "error")
            return redirect(request.referrer or url_for('visualise_data'))

        if request.method == 'POST':
            try:
                entry.category = request.form['category']
                entry.units = float(request.form['field_one'])
                entry.cost_per_unit = float(request.form['field_two'])
                entry.start_date = date.fromisoformat(request.form['start_date'])
                entry.end_date = date.fromisoformat(request.form['end_date'])
            except (ValueError, TypeError):
                flash("Invalid data; please try again.", "error")
                return redirect(request.referrer or url_for('visualise_data'))
            db.session.commit()
            flash("Bill updated!", "success")
            return redirect(request.referrer or url_for('visualise_data'))

        return render_template('edit_bill.html', bill=entry)

    @app.route('/history')
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

