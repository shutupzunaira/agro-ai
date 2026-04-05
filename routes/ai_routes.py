"""
routes/ai_routes.py — AI feature routes (FINAL UPGRADED VERSION)

This includes:
1. Crop recommendation
2. Weed detection (CNN)
3. Smart decision layer for Agro-AI system
"""

import os
from flask import Blueprint, render_template, request

from ai.predictor import predict_crop
from ai.model import predict_weed_or_crop

ai_bp = Blueprint("ai", __name__)

UPLOAD_FOLDER = "static/uploads"


# =========================
# 🌾 Crop Recommendation
# =========================
@ai_bp.route("/recommend", methods=["POST"])
def recommend():
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

        return render_template(
            "home.html",
            crop_result=f"{crop} ({confidence:.2f})"
        )

    except Exception as e:
        print("❌ Crop recommendation error:", e)
        return render_template("home.html", error="Something went wrong")


# =========================
# 🌱 Weed Detection + AI Decision Layer
# =========================
@ai_bp.route("/weed-detect", methods=["POST"])
def weed_detect():
    try:
        # Check file
        if "image" not in request.files:
            return render_template("home.html", error="No image uploaded")

        file = request.files["image"]

        if file.filename == "":
            return render_template("home.html", error="No file selected")

        # Ensure upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Save file safely
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # =========================
        # 🧠 AI MODEL PREDICTION
        # =========================
        result = predict_weed_or_crop(filepath)

        label = result.get("label", "Unknown")
        confidence = result.get("confidence", 0.0)
        suggestion = result.get("suggestion", "No suggestion available")

        # =========================
        # 🌿 SMART DECISION LAYER
        # =========================
        if label.lower() == "weed" and confidence >= 0.85:
            action = "🚨 High weed density → Targeted removal recommended"
        elif label.lower() == "weed":
            action = "⚠️ Weed detected → Monitor field or selective removal"
        elif label.lower() == "crop":
            action = "✅ Healthy crop → No action needed"
        else:
            action = "🌿 Uncertain → Retake clearer image"

        # =========================
        # 📤 SEND TO FRONTEND
        # =========================
        return render_template(
            "home.html",
            prediction=label,
            confidence=f"{confidence * 100:.2f}%",
            suggestion=suggestion,
            action=action,
            image_path=filepath
        )

    except Exception as e:
        print("❌ Weed detection error:", e)
        return render_template("home.html", error="Something went wrong")