"""
routes/ai_routes.py — AI feature routes
"""

import os
from flask import Blueprint, render_template, request, current_app, redirect, url_for
from flask_login import login_required, current_user
from PIL import Image
import numpy as np

from ai.predictor import predict_crop
from ai.model import WEED_IMG_SIZE, predict_weed_or_crop

ai_bp = Blueprint("ai", __name__)

UPLOAD_FOLDER = "static/uploads"


# =========================
# 🌾 Crop Recommendation
# =========================
@ai_bp.route("/recommend", methods=["GET", "POST"])
def recommend():
    if request.method == "GET":
        return redirect(url_for("dashboard.index"))

    try:
        inputs = {
            "N": float(request.form.get("N")),
            "P": float(request.form.get("P")),
            "K": float(request.form.get("K")),
            "temperature": float(request.form.get("temperature")),
            "humidity": float(request.form.get("humidity")),
            "ph": float(request.form.get("ph")),
            "rainfall": float(request.form.get("rainfall")),
        }

        crop, confidence = predict_crop(inputs)

        from flask import flash
        flash(f"AI recommends: {crop} ({confidence*100:.0f}% confidence).", "success")
        return redirect(url_for("dashboard.index"))

    except Exception as e:
        print("❌ Crop recommendation error:", e)
        from flask import flash
        flash("Crop recommendation failed. Check your inputs.", "error")
        return redirect(url_for("dashboard.index"))


# =========================
# 🌱 Weed Detection
# =========================
@ai_bp.route("/weed-detect", methods=["POST"])
def weed_detect():
    try:
        # Check file
        from flask import session
        if "image" not in request.files:
            session['weed_error'] = "No image uploaded. Choose a file or capture with the camera."
            return redirect(url_for('dashboard.index'))

        file = request.files["image"]

        if file.filename == "":
            session['weed_error'] = "No file selected."
            return redirect(url_for('dashboard.index'))

        img = Image.open(file).convert("RGB")
        img = img.resize(WEED_IMG_SIZE)
        img_array = np.array(img, dtype=np.float32) / 255.0

        label, confidence = predict_weed_or_crop(img_array)

        # Suggestion logic
        if label == "weed":
            suggestion = "Remove weeds manually or use selective herbicide"
        else:
            suggestion = "Crop is healthy"

        # Action logic
        if label == "weed" and confidence > 0.85:
            action = "🚨 High weed density → Immediate removal"
        elif label == "weed":
            action = "⚠️ Weed detected → Monitor field"
        else:
            action = "✅ No action needed"

        from flask import session
        session['weed_result'] = {
            'prediction': label,
            'confidence': f"{confidence * 100:.2f}%",
            'suggestion': suggestion,
            'action': action
        }
        return redirect(url_for('dashboard.index'))

    except ImportError as e:
        print("❌ Weed model:", e)
        from flask import session
        session['weed_error'] = "Weed detection needs TensorFlow. Install it in this environment: pip install tensorflow"
        return redirect(url_for('dashboard.index'))
    except FileNotFoundError as e:
        print("❌ Weed model:", e)
        from flask import session
        session['weed_error'] = "Weed detection is not configured yet. Add your trained weed_crop_model.h5 file to the ai/ folder."
        return redirect(url_for('dashboard.index'))
    except Exception as e:
        print("❌ Weed detection error:", e)
        from flask import session
        session['weed_error'] = "Could not analyze this image. Try another photo (JPG or PNG, under 5 MB)."
        return redirect(url_for('dashboard.index'))


# =========================
# 🍃 Disease Detection
# =========================
@ai_bp.route("/disease", methods=["GET", "POST"])
@login_required
def disease():
    if request.method == "GET":
        return render_template("disease.html", result=None)

    try:
        if "image" not in request.files:
            return render_template("disease.html", result=None,
                                   error="No image uploaded.")

        file = request.files["image"]
        if file.filename == "":
            return render_template("disease.html", result=None,
                                   error="No file selected.")

        # ── Save uploaded image ───────────────────────────────────────────────
        upload_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_dir, exist_ok=True)

        from werkzeug.utils import secure_filename
        filename    = secure_filename(file.filename)
        save_name   = f"{current_user.id}_{filename}"
        save_path   = os.path.join(upload_dir, save_name)
        file.save(save_path)

        relative_path = f"uploads/{save_name}"

        # ── Run disease detection ─────────────────────────────────────────────
        from ai.disease_detector import detect_disease
        info = detect_disease(save_path)   # returns a dict

        # ── Save to database ──────────────────────────────────────────────────
        from extensions import db
        from models import DiseaseReport
        report = DiseaseReport(
            user_id      = current_user.id,
            image_path   = relative_path,
            disease_name = info["disease"],
            confidence   = info["confidence"],
            treatment    = info["treatment"],
        )
        db.session.add(report)
        db.session.commit()

        result = {**info, "image_path": relative_path}
        return render_template("disease.html", result=result)

    except Exception as e:
        print("❌ Disease detection error:", e)
        return render_template("disease.html", result=None,
                               error="Analysis failed. Please try another photo.")