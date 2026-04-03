from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
def home():
    return render_template("home.html")

@pages_bp.route("/about")
def about():
    return render_template("about.html")