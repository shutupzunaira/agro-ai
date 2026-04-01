# AgriSense — AI Agriculture Website

A full-stack local web application for AI-powered crop recommendations,
disease detection, soil dashboards, and agricultural articles.

---

## Project structure

```
agri/
├── app.py                  ← Flask entry point (start here)
├── extensions.py           ← Shared db & login_manager objects
├── models.py               ← Database tables (User, SoilReading, DiseaseReport, BlogPost)
├── requirements.txt
│
├── routes/                 ← URL route handlers (one file per feature)
│   ├── pages.py            ← / and /about
│   ├── auth.py             ← /auth/register, /auth/login, /auth/logout
│   ├── dashboard.py        ← /dashboard/
│   ├── ai_routes.py        ← /ai/recommend, /ai/disease
│   └── blog.py             ← /blog/, /blog/<slug>
│
├── ai/                     ← Machine learning modules
│   ├── predictor.py        ← Crop recommendation (Random Forest)
│   └── disease_detector.py ← Leaf disease detection (image analysis)
│
├── templates/              ← Jinja2 HTML templates
│   ├── base.html           ← Shared layout (nav, flash, footer)
│   ├── home.html           ← Landing page
│   ├── about.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   └── index.html      ← Charts + soil history table
│   ├── ai/
│   │   ├── recommend.html  ← Crop prediction form
│   │   └── disease.html    ← Image upload + detection result
│   └── blog/
│       ├── index.html      ← Article listing
│       └── article.html    ← Single article
│
└── static/
    ├── css/main.css        ← All styles (organic dark theme)
    └── uploads/            ← Uploaded leaf images (auto-created)
```

---

## Setup (5 minutes)

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py
```

Open **http://localhost:5000** in your browser.

To access it from another device on your local network:
```bash
# Find your local IP
ip addr show          # Linux/Mac
ipconfig              # Windows
# Then visit: http://<your-ip>:5000
```

---

## Learning path

Work through these files in order to understand how it all connects:

| Step | File | What you learn |
|------|------|---------------|
| 1 | `extensions.py` | Why we separate db from app.py (circular imports) |
| 2 | `models.py` | SQLAlchemy ORM — Python classes as database tables |
| 3 | `app.py` | Flask factory pattern, blueprints, config |
| 4 | `routes/auth.py` | GET vs POST, form data, password hashing, sessions |
| 5 | `routes/dashboard.py` | `@login_required`, querying the DB, passing data to templates |
| 6 | `templates/dashboard/index.html` | Jinja2 syntax, Chart.js integration |
| 7 | `ai/predictor.py` | scikit-learn, model persistence with pickle |
| 8 | `routes/ai_routes.py` | File uploads, calling ML models from routes |
| 9 | `ai/disease_detector.py` | Image processing with Pillow, upgrade to CNN |

---

## Security overview

| Threat | Defence |
|--------|---------|
| Plain-text passwords | Werkzeug `generate_password_hash` (PBKDF2-SHA256) |
| SQL injection | SQLAlchemy parameterised queries (never raw SQL) |
| Unauthorised access | `@login_required` on every protected route |
| Session forgery | Flask `SECRET_KEY` signs session cookies with HMAC |
| File upload abuse | UUID filenames, extension whitelist, 5 MB size limit |
| Path traversal | `werkzeug.utils.secure_filename` on all uploads |

**Before going to production:**
```bash
export SECRET_KEY="replace-with-64-random-chars"
# Turn off debug mode in app.py: debug=False
```

---

## Upgrading the AI models

### Crop recommendation
Replace `_build_sample_dataset()` in `ai/predictor.py` with:
```python
import pandas as pd
df = pd.read_csv("data/Crop_recommendation.csv")
X  = df[["N","P","K","temperature","humidity","ph","rainfall"]].values
y  = le.fit_transform(df["label"])
```
Download dataset: **Kaggle → "Crop Recommendation Dataset"** (2,200 rows, 22 crops)

### Disease detection
Replace `_analyse_image_colours()` in `ai/disease_detector.py` with a
PyTorch CNN trained on the **PlantVillage dataset** (54,000 leaf images, 38 classes).

---

## Adding a blog post (Flask shell)

```bash
flask shell
>>> from app import create_app; app = create_app()
>>> from extensions import db
>>> from models import BlogPost
>>> with app.app_context():
...     p = BlogPost(title="My post", slug="my-post",
...                  summary="Short summary", body="<p>Full HTML body</p>", tag="Soil")
...     db.session.add(p); db.session.commit()
```
