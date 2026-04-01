"""
routes/dashboard.py — User dashboard.

Shows:
  - Soil + weather readings history (last 10 entries)
  - Chart data (sent as JSON so Chart.js can draw it in the browser)
  - A form to log a new soil reading
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import SoilReading, DiseaseReport

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required   # @login_required redirects to login page if user is not authenticated
def index():
    # Fetch this user's last 10 soil readings, newest first
    readings = (
        SoilReading.query
        .filter_by(user_id=current_user.id)
        .order_by(SoilReading.recorded_at.desc())
        .limit(10)
        .all()
    )

    # Fetch last 5 disease reports for the sidebar
    disease_history = (
        DiseaseReport.query
        .filter_by(user_id=current_user.id)
        .order_by(DiseaseReport.submitted_at.desc())
        .limit(5)
        .all()
    )

    # ── Build chart data ──────────────────────────────────────────────────────
    # We reverse the list so the chart shows oldest → newest (left to right).
    chart_readings = list(reversed(readings))

    chart_data = {
        # Labels = date strings for the x-axis
        "labels": [r.recorded_at.strftime("%d %b") for r in chart_readings],

        # Datasets: one line per metric
        "ph":          [r.ph          for r in chart_readings],
        "nitrogen":    [r.nitrogen    for r in chart_readings],
        "phosphorus":  [r.phosphorus  for r in chart_readings],
        "potassium":   [r.potassium   for r in chart_readings],
        "temperature": [r.temperature for r in chart_readings],
        "humidity":    [r.humidity    for r in chart_readings],
    }

    # json.dumps converts the Python dict → a JSON string so Jinja2 can
    # embed it directly in a <script> tag in the HTML template.
    chart_json = json.dumps(chart_data)

    return render_template(
        "dashboard/index.html",
        readings=readings,
        disease_history=disease_history,
        chart_json=chart_json,
    )


@dashboard_bp.route("/log", methods=["POST"])
@login_required
def log_reading():
    """
    Receives a form submission with soil + weather values,
    saves a new SoilReading to the database.
    """
    try:
        reading = SoilReading(
            user_id     = current_user.id,
            nitrogen    = float(request.form["nitrogen"]),
            phosphorus  = float(request.form["phosphorus"]),
            potassium   = float(request.form["potassium"]),
            ph          = float(request.form["ph"]),
            temperature = float(request.form["temperature"]),
            humidity    = float(request.form["humidity"]),
            rainfall    = float(request.form["rainfall"]),
        )
        db.session.add(reading)
        db.session.commit()
        flash("Reading saved to dashboard.", "success")
    except (ValueError, KeyError) as e:
        flash(f"Invalid data: {e}", "error")

    return redirect(url_for("dashboard.index"))
