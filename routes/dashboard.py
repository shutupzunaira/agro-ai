"""
routes/dashboard.py — Authenticated user dashboard.

All AI features live here after login:
  - Crop recommendation (with weather/location)
  - Weed detection
  - Disease detection
  - Soil & weather tracking (chart + form)
  - Articles & insights
"""

import json
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, jsonify,
)
from flask_login import login_required, current_user
from extensions import db
from models import SoilReading, DiseaseReport, BlogPost

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    # ── Soil readings ─────────────────────────────────────────────────────────
    readings = (
        SoilReading.query
        .filter_by(user_id=current_user.id)
        .order_by(SoilReading.recorded_at.desc())
        .limit(10)
        .all()
    )

    # ── Disease reports ───────────────────────────────────────────────────────
    disease_history = (
        DiseaseReport.query
        .filter_by(user_id=current_user.id)
        .order_by(DiseaseReport.submitted_at.desc())
        .limit(5)
        .all()
    )

    # ── Chart data ────────────────────────────────────────────────────────────
    chart_readings = list(reversed(readings))
    chart_data = {
        "labels":      [r.recorded_at.strftime("%d %b") for r in chart_readings],
        "ph":          [r.ph          for r in chart_readings],
        "nitrogen":    [r.nitrogen    for r in chart_readings],
        "phosphorus":  [r.phosphorus  for r in chart_readings],
        "potassium":   [r.potassium   for r in chart_readings],
        "temperature": [r.temperature for r in chart_readings],
        "humidity":    [r.humidity    for r in chart_readings],
        "rainfall":    [r.rainfall    for r in chart_readings],
    }
    chart_json = json.dumps(chart_data)

    # ── Articles ──────────────────────────────────────────────────────────────
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(6).all()

    from flask import session
    weed_result = session.pop('weed_result', None)
    weed_error = session.pop('weed_error', None)

    return render_template(
        "dashboard/index.html",
        readings=readings,
        disease_history=disease_history,
        chart_json=chart_json,
        posts=posts,
        prediction=weed_result['prediction'] if weed_result else None,
        confidence=weed_result['confidence'] if weed_result else None,
        suggestion=weed_result['suggestion'] if weed_result else None,
        action=weed_result['action'] if weed_result else None,
        weed_error=weed_error
    )


# ── Weather endpoint (called via JS fetch) ────────────────────────────────────
@dashboard_bp.route("/weather")
@login_required
def weather():
    """Return current weather JSON for a lat/lng pair."""
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng required"}), 400

    from ai.weather import fetch_weather
    data = fetch_weather(lat, lng)
    return jsonify(data)


# ── Log soil reading ──────────────────────────────────────────────────────────
@dashboard_bp.route("/log", methods=["POST"])
@login_required
def log_reading():
    try:
        nitrogen    = float(request.form["nitrogen"])
        phosphorus  = float(request.form["phosphorus"])
        potassium   = float(request.form["potassium"])
        ph          = float(request.form["ph"])
        temperature = float(request.form["temperature"])
        humidity    = float(request.form["humidity"])
        rainfall    = float(request.form["rainfall"])

        reading = SoilReading(
            user_id=current_user.id,
            nitrogen=nitrogen, phosphorus=phosphorus, potassium=potassium,
            ph=ph, temperature=temperature, humidity=humidity, rainfall=rainfall,
        )

        # ── Run AI crop prediction ────────────────────────────────────────────
        try:
            from ai.predictor import predict_crop
            crop, confidence = predict_crop({
                "N": nitrogen, "P": phosphorus, "K": potassium,
                "temperature": temperature, "humidity": humidity,
                "ph": ph, "rainfall": rainfall,
            })
            reading.recommended_crop = crop
            reading.confidence       = confidence
            flash(f"Reading saved. AI recommends: {crop} ({confidence*100:.0f}%).", "success")
        except Exception as ai_err:
            print(f"⚠️ Crop prediction skipped: {ai_err}")
            flash("Reading saved (crop prediction unavailable).", "info")

        db.session.add(reading)
        db.session.commit()

    except (ValueError, KeyError) as e:
        flash(f"Invalid data: {e}", "error")

    return redirect(url_for("dashboard.index"))
