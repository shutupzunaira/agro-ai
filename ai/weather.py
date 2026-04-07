"""
ai/weather.py — Fetch current weather from Open-Meteo (free, no API key).

Returns temperature, humidity, rainfall, wind speed, and a human description.
Also does reverse geocoding via Open-Meteo's geocoding API.
"""

import urllib.request
import json
import ssl

# macOS Python often lacks SSL certs — use unverified for public APIs
_SSL_CTX = ssl._create_unverified_context()


def fetch_weather(lat: float, lng: float) -> dict:
    """
    Call Open-Meteo for current weather at the given coordinates.
    Returns a dict with: temperature, humidity, rainfall, wind_speed,
    weather_code, description, location_name.
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lng}"
            f"&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,weather_code"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "AgriSense/1.0"})
        with urllib.request.urlopen(req, timeout=8, context=_SSL_CTX) as resp:
            data = json.loads(resp.read().decode())

        current = data.get("current", {})

        weather_code = current.get("weather_code", 0)
        description = _weather_code_to_text(weather_code)

        result = {
            "temperature": current.get("temperature_2m", 0),
            "humidity":    current.get("relative_humidity_2m", 0),
            "rainfall":    current.get("rain", 0),
            "wind_speed":  current.get("wind_speed_10m", 0),
            "weather_code": weather_code,
            "description": description,
            "lat": lat,
            "lng": lng,
            "location_name": _reverse_geocode(lat, lng),
        }
        return result

    except Exception as e:
        print(f"⚠️ Weather API error: {e}")
        return {
            "temperature": 0, "humidity": 0, "rainfall": 0,
            "wind_speed": 0, "weather_code": -1,
            "description": "Weather data unavailable",
            "lat": lat, "lng": lng,
            "location_name": f"{lat:.2f}°, {lng:.2f}°",
        }


def _reverse_geocode(lat: float, lng: float) -> str:
    """Best-effort reverse geocode using Open-Meteo geocoding."""
    try:
        url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?latitude={lat}&longitude={lng}"
            f"&name={lat},{lng}&count=1"
        )
        # Fallback: use Nominatim for reverse geocoding
        nom_url = (
            f"https://nominatim.openstreetmap.org/reverse"
            f"?lat={lat}&lon={lng}&format=json&zoom=10"
        )
        req = urllib.request.Request(nom_url, headers={
            "User-Agent": "AgriSense/1.0 (educational project)"
        })
        with urllib.request.urlopen(req, timeout=5, context=_SSL_CTX) as resp:
            data = json.loads(resp.read().decode())

        addr = data.get("address", {})
        parts = []
        for key in ("city", "town", "village", "county", "state"):
            if key in addr:
                parts.append(addr[key])
                if len(parts) >= 2:
                    break
        if not parts and "display_name" in data:
            parts = [data["display_name"].split(",")[0]]
        return ", ".join(parts) if parts else f"{lat:.2f}°, {lng:.2f}°"

    except Exception:
        return f"{lat:.2f}°, {lng:.2f}°"


def _weather_code_to_text(code: int) -> str:
    """WMO weather code → human-readable text."""
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
        3: "Overcast", 45: "Foggy", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers",
        82: "Violent rain showers", 95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "Unknown")
