"""
routes/auth.py — Authentication routes.

Handles: registration, login, logout.
All routes are grouped under the "auth" blueprint, so their URLs
will be /auth/register, /auth/login, /auth/logout (set in app.py).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    GET  → show the registration page.
    POST → read the submitted form, validate, create user, redirect to login.
    """
    if current_user.is_authenticated:
        return redirect(url_for("pages.home"))  # already logged in

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm",  "")

        # ── Validation ────────────────────────────────────────────────────────
        if not all([username, email, password]):
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "error")
            return redirect(url_for("auth.register"))

        # ── Create user ───────────────────────────────────────────────────────
        user = User(username=username, email=email)
        user.set_password(password)   # hashes before storing
        db.session.add(user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            # Send user to the page they originally tried to visit, or dashboard
            next_page = request.args.get("next") or url_for("dashboard.index")
            return redirect(next_page)

        flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("pages.home"))
