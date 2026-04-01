"""
app.py — The entry point for AgriSense.

Flask uses an "application factory" pattern here: create_app() builds
and configures the app. This makes it easy to test and to run with
different configs (development vs production) later.
"""

from flask import Flask
from extensions import db, login_manager
from routes.pages   import pages_bp
from routes.auth    import auth_bp
from routes.ai_routes import ai_bp
from routes.blog    import blog_bp
from routes.dashboard import dashboard_bp
import os


def create_app():
    app = Flask(__name__)

    # ── Configuration ────────────────────────────────────────────────────────
    # SECRET_KEY signs session cookies. Change this to a long random string
    # in production. Best practice: set it as an environment variable.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me-123")

    # SQLite creates a local file called agri.db in this folder.
    # No separate database server needed — perfect for local development.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agri.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # suppresses a noisy warning

    # Where uploaded images (disease detection) will be saved
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit

    # ── Wire up extensions ────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # where to redirect unauthenticated users

    # ── Register blueprints (route groups) ───────────────────────────────────
    # Each blueprint is a separate file with its own set of routes.
    # url_prefix means all routes in that blueprint start with that path.
    app.register_blueprint(pages_bp)                      # /  and  /about
    app.register_blueprint(auth_bp,      url_prefix="/auth")     # /auth/login  etc.
    app.register_blueprint(ai_bp,        url_prefix="/ai")       # /ai/disease  etc.
    app.register_blueprint(blog_bp,      url_prefix="/blog")     # /blog/  etc.
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")# /dashboard/

    # ── Create database tables ────────────────────────────────────────────────
    # db.create_all() reads all Model classes and creates the tables if they
    # don't already exist. Safe to call every startup — won't delete data.
    with app.app_context():
        db.create_all()
        _seed_demo_data()   # add sample blog posts on first run

    return app


def _seed_demo_data():
    """Add a couple of demo blog posts if the table is empty."""
    from models import BlogPost
    if BlogPost.query.count() == 0:
        demo = [
            BlogPost(
                title   = "How AI is changing crop yield prediction",
                slug    = "ai-crop-yield-prediction",
                summary = "A look at how machine learning models trained on satellite and soil data are outperforming traditional agronomic models.",
                body    = "<p>Machine learning models can now process terabytes of satellite imagery, soil sensor readings, and historical yield data to produce hyper-local crop recommendations...</p><p>The key breakthrough was combining convolutional neural networks (for imagery) with gradient-boosted trees (for tabular sensor data) into an ensemble model...</p>",
                tag     = "Technology",
            ),
            BlogPost(
                title   = "Reading soil pH: what the numbers mean",
                slug    = "soil-ph-guide",
                summary = "pH affects nutrient availability more than almost any other factor. Here's how to interpret your readings and what to do about them.",
                body    = "<p>Soil pH runs on a scale of 0–14. Most crops prefer 6.0–7.0, the 'slightly acidic to neutral' range where nutrients like phosphorus and calcium are most soluble...</p><p>If your pH drops below 5.5, consider agricultural lime. If it rises above 7.5, elemental sulphur can help...</p>",
                tag     = "Soil Science",
            ),
            BlogPost(
                title   = "Understanding the NPK fertiliser ratio",
                slug    = "npk-fertiliser-guide",
                summary = "Nitrogen, Phosphorus, and Potassium each play a distinct role. Knowing which to apply when can double your output.",
                body    = "<p>The three numbers on a fertiliser bag (e.g. 10-20-10) represent the percentage by weight of N, P₂O₅, and K₂O respectively...</p><p>Nitrogen drives leaf and stem growth. Phosphorus is critical for root development and flowering. Potassium strengthens cell walls and improves drought resistance...</p>",
                tag     = "Fertilisers",
            ),
        ]
        from extensions import db
        db.session.add_all(demo)
        db.session.commit()


# ── Run the server ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    # host="0.0.0.0" makes the server reachable on your local network,
    # not just from localhost. Other devices can visit http://<your-ip>:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
