"""
routes/ai_routes.py — AI feature routes.

Two features:
  1. /ai/recommend  — Crop recommendation (soil + climate inputs → model → crop name)
  2. /ai/disease    — Disease detection   (upload leaf image → model → disease name)
"""

import os
import json
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import SoilReading, DiseaseReport
from ai.predictor import predict_crop
from ai.disease_detector import detect_disease

ai_bp = Blueprint("ai", __name__)

# File types we accept for image uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename: str) -> bool:
    """Return True if the uploaded file has an acceptable extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────────────────────────────────────
#  CROP RECOMMENDATION
# ─────────────────────────────────────────────────────────────────────────────
@ai_bp.route("/recommend", methods=["GET", "POST"])
@login_required
def recommend():
    result = None

    if request.method == "POST":
        try:
            inputs = {
                "N":           float(request.form["nitrogen"]),
                "P":           float(request.form["phosphorus"]),
                "K":           float(request.form["potassium"]),
                "temperature": float(request.form["temperature"]),
                "humidity":    float(request.form["humidity"]),
                "ph":          float(request.form["ph"]),
                "rainfall":    float(request.form["rainfall"]),
            }

            crop, confidence = predict_crop(inputs)

            # Save to the database so it appears in the dashboard history
            reading = SoilReading(
                user_id          = current_user.id,
                nitrogen         = inputs["N"],
                phosphorus       = inputs["P"],
                potassium        = inputs["K"],
                ph               = inputs["ph"],
                temperature      = inputs["temperature"],
                humidity         = inputs["humidity"],
                rainfall         = inputs["rainfall"],
                recommended_crop = crop,
                confidence       = confidence,
            )
            db.session.add(reading)
            db.session.commit()

            result = {"crop": crop, "confidence": confidence}

        except (ValueError, KeyError) as e:
            flash(f"Please fill in all fields correctly. ({e})", "error")

    return render_template("ai/recommend.html", result=result)


# ─────────────────────────────────────────────────────────────────────────────
#  DISEASE DETECTION
# ─────────────────────────────────────────────────────────────────────────────
@ai_bp.route("/disease", methods=["GET", "POST"])
@login_required
def disease():
    result = None

    if request.method == "POST":
        # 1. Check a file was actually attached
        if "image" not in request.files or request.files["image"].filename == "":
            flash("Please select an image to upload.", "error")
            return redirect(url_for("ai.disease"))

        file = request.files["image"]

        if not allowed_file(file.filename):
            flash("Only PNG, JPG, JPEG, or WEBP images are accepted.", "error")
            return redirect(url_for("ai.disease"))

        # 2. Save the file with a UUID name (prevents path-traversal attacks)
        ext       = file.filename.rsplit(".", 1)[1].lower()
        safe_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)

        # 3. Run the AI model
        disease_name, confidence, treatment = detect_disease(save_path)

        # 4. Save the report
        report = DiseaseReport(
            user_id      = current_user.id,
            image_path   = f"uploads/{safe_name}",
            disease_name = disease_name,
            confidence   = confidence,
            treatment    = treatment,
        )
        db.session.add(report)
        db.session.commit()

        result = {
            "disease":    disease_name,
            "confidence": confidence,
            "treatment":  treatment,
            "image_path": f"uploads/{safe_name}",
        }

    return render_template("ai/disease.html", result=result)
