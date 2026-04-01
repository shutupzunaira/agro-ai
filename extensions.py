"""
extensions.py — Shared Flask extension objects.

WHY THIS FILE EXISTS:
If we created db = SQLAlchemy() inside app.py, and then models.py tried to
import db from app.py, Python would have a "circular import" problem:
  app.py imports models → models.py imports app.py → infinite loop.

The fix: create the extension objects here (in a neutral file), then
import them in both app.py (to call init_app) and models.py (to define tables).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# db is the database connection object.
# We call db.init_app(app) in create_app() to attach it to the Flask app.
db = SQLAlchemy()

# login_manager tracks which user is currently logged in via their session cookie.
login_manager = LoginManager()
