from flask import Flask, render_template, request, flash, redirect, url_for
from app import application, db
from app.models import BillEntry
from datetime import date 

# Homepage route
@application.route("/")
@application.route("/home")
def home():
    return render_template("landingpage.html")

# Login/signup page
@application.route("/login")
def login():
    return render_template("login-signup.html")

@application.route("/profile")
def profile():
    return render_template("profile.html")

@application.route("/upload", methods=["GET", "POST"])
def uploadpage():
    if request.method == "POST":
        # pull values from the form
        category      = request.form.get("category")
        units_str     = request.form.get("field_one", "").strip()
        cost_str      = request.form.get("field_two", "").strip()
        start_str     = request.form.get("start_date")
        end_str       = request.form.get("end_date")

        # validate & convert
        try:
            units = float(units_str)
            cost  = float(cost_str)
            # parse ISO strings into date objects
            start_date = date.fromisoformat(start_str)
            end_date   = date.fromisoformat(end_str)
        except ValueError:
            flash("Units and cost must be numbers.", "error")
            return redirect(url_for("uploadpage"))

        # create and save the entry
        entry = BillEntry(
            user_id       = 1,                  # swap to current_user.id once you have auth
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
