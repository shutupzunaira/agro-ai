"""
app.py — Entry point for AgriSense
"""

from flask import Flask
from extensions import db, login_manager

from routes.pages import pages_bp
from routes.auth import auth_bp
from routes.ai_routes import ai_bp
from routes.blog import blog_bp
from routes.dashboard import dashboard_bp

import os


def create_app():
    app = Flask(__name__)

    # ── Config ─────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-secret-change-me-123"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agri.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "uploads"
    )
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    # ── Extensions ─────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = None

    # ── Blueprints ─────────────────────────
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # ── DB Init ────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_demo_data()

    return app


def _seed_demo_data():
    from models import BlogPost
    from extensions import db

    if BlogPost.query.count() == 0:
        demo = [
            BlogPost(
                title="How AI is changing crop yield prediction",
                slug="ai-crop-yield-prediction",
                summary="ML models improve farming decisions.",
                body="<p>AI improves agriculture...</p>",
                tag="Technology",
            ),
        ]
        db.session.add_all(demo)
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)