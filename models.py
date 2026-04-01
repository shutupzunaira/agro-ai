"""
models.py — Database table definitions.

Each Python class here = one table in the SQLite database.
Each class attribute = one column.
SQLAlchemy translates these classes into SQL CREATE TABLE statements.
"""

from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ═══════════════════════════════════════════════════════
#  USER
# ═══════════════════════════════════════════════════════
class User(UserMixin, db.Model):
    """
    Registered users.

    UserMixin is a helper class from Flask-Login that provides four
    required methods: is_authenticated, is_active, is_anonymous, get_id.
    We get them for free by inheriting from it.
    """
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships: one user → many of these records
    soil_readings    = db.relationship("SoilReading",    backref="user", lazy=True)
    disease_reports  = db.relationship("DiseaseReport",  backref="user", lazy=True)

    def set_password(self, raw_password: str):
        """
        Hash the password using PBKDF2-SHA256 before storing.
        NEVER store plain-text passwords — if your DB leaks, hashes
        are useless to an attacker without the original text.
        """
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        Compare a submitted password against the stored hash.
        Returns True if they match, False otherwise.
        """
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: str):
    """
    Flask-Login calls this function on every request to load the
    currently logged-in user from the database, using the ID stored
    in their session cookie.
    """
    return User.query.get(int(user_id))


# ═══════════════════════════════════════════════════════
#  SOIL READING  (dashboard data)
# ═══════════════════════════════════════════════════════
class SoilReading(db.Model):
    """
    A single soil + weather measurement submitted by a user.
    Used to populate the dashboard charts and feed the AI model.
    """
    __tablename__ = "soil_readings"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Soil nutrient values
    nitrogen    = db.Column(db.Float, nullable=False)   # kg/ha
    phosphorus  = db.Column(db.Float, nullable=False)
    potassium   = db.Column(db.Float, nullable=False)
    ph          = db.Column(db.Float, nullable=False)   # 0–14 scale

    # Climate values
    temperature = db.Column(db.Float, nullable=False)   # °C
    humidity    = db.Column(db.Float, nullable=False)   # %
    rainfall    = db.Column(db.Float, nullable=False)   # mm

    # AI output (stored after prediction)
    recommended_crop = db.Column(db.String(100))
    confidence       = db.Column(db.Float)              # 0.0–1.0

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SoilReading pH={self.ph} crop={self.recommended_crop}>"


# ═══════════════════════════════════════════════════════
#  DISEASE REPORT  (image-based AI detection)
# ═══════════════════════════════════════════════════════
class DiseaseReport(db.Model):
    """
    Stores the result of an uploaded crop image analysed for disease.
    """
    __tablename__ = "disease_reports"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    image_path   = db.Column(db.String(300), nullable=False)  # path inside static/uploads/
    disease_name = db.Column(db.String(200))
    confidence   = db.Column(db.Float)
    treatment    = db.Column(db.Text)   # recommended treatment text
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DiseaseReport {self.disease_name} {self.confidence:.0%}>"


# ═══════════════════════════════════════════════════════
#  BLOG POST
# ═══════════════════════════════════════════════════════
class BlogPost(db.Model):
    """
    Articles written by the site admin.
    In a full CMS you'd add an admin panel — for now, posts are
    added via _seed_demo_data() in app.py or directly via Flask shell.
    """
    __tablename__ = "blog_posts"

    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    slug       = db.Column(db.String(200), unique=True, nullable=False)  # URL-friendly title
    summary    = db.Column(db.Text, nullable=False)   # shown on listing page
    body       = db.Column(db.Text, nullable=False)   # full HTML content
    tag        = db.Column(db.String(60))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BlogPost '{self.title}'>"
