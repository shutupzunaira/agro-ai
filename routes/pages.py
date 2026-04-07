"""
routes/pages.py — Public pages (no login required).
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from models import BlogPost

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    # If logged in, go straight to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    # Fetch latest articles for the landing page
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(6).all()
    return render_template("home.html", posts=posts)


@pages_bp.route("/about")
def about():
    return render_template("about.html")