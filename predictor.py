"""
ai/predictor.py — Crop recommendation model.

HOW IT WORKS:
  1. We define a small training dataset (soil + climate → crop label).
  2. We train a Random Forest classifier on it.
  3. We save the trained model to a .pkl file using pickle.
  4. On future calls, we load from .pkl instead of retraining every time.

TO USE THE REAL DATASET:
  Download "Crop Recommendation Dataset" from Kaggle, put it at data/crops.csv,
  then replace the _build_sample_dataset() section with:
      import pandas as pd
      df = pd.read_csv("data/crops.csv")
      X  = df[FEATURES].values
      y  = le.fit_transform(df["label"])
"""

import os
import pickle
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_model.pkl")

# These must be in the exact order the model was trained on
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def _build_sample_dataset():
    """
    Returns (X, label_strings) for a tiny demo dataset.
    Replace this function with a real CSV load for production accuracy.
    """
    rows = [
        # N,  P,  K,  temp, humid,  ph,  rain,   crop
        [90, 42, 43, 20.8, 82.0, 6.5, 202.9, "rice"],
        [85, 58, 41, 21.7, 80.3, 7.0, 226.6, "rice"],
        [80, 47, 40, 22.0, 81.0, 6.8, 210.0, "rice"],
        [60, 55, 44, 23.0, 82.3, 7.8, 263.9, "maize"],
        [74, 35, 40, 26.5, 80.0, 6.9,  85.4, "maize"],
        [78, 42, 42, 24.0, 79.0, 6.7,  90.0, "maize"],
        [20, 30, 10, 25.0, 58.5, 5.8,  72.0, "wheat"],
        [22, 28, 12, 27.0, 56.0, 5.5,  68.0, "wheat"],
        [24, 31, 11, 26.0, 57.0, 5.6,  70.0, "wheat"],
        [14, 12, 14, 27.0, 54.0, 6.9,  40.0, "cotton"],
        [15, 11, 13, 28.5, 55.0, 7.0,  45.0, "cotton"],
        [13, 10, 15, 29.0, 53.0, 7.1,  38.0, "cotton"],
        [50, 53, 48, 27.0, 66.0, 6.0, 140.0, "sugarcane"],
        [52, 55, 50, 26.5, 68.0, 6.1, 135.0, "sugarcane"],
        [30, 60, 55, 18.0, 45.0, 6.5,  65.0, "chickpea"],
        [28, 58, 52, 19.5, 44.0, 6.4,  60.0, "chickpea"],
        [40, 40, 35, 30.0, 75.0, 6.0, 120.0, "mango"],
        [38, 38, 34, 31.0, 74.0, 5.9, 125.0, "mango"],
        [25, 50, 45, 22.0, 70.0, 6.2,  95.0, "lentil"],
        [26, 52, 46, 21.5, 69.0, 6.3,  90.0, "lentil"],
    ]
    X      = np.array([r[:7] for r in rows])
    labels = [r[7] for r in rows]
    return X, labels


def _train_and_save():
    """Train a Random Forest and pickle it to disk."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder

    X, labels = _build_sample_dataset()

    le = LabelEncoder()
    y  = le.fit_transform(labels)

    # n_estimators = number of trees in the forest
    # More trees → more accurate but slower to train
    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": clf, "encoder": le}, f)

    print(f"[Crop model] Trained and saved → {MODEL_PATH}")
    return clf, le


def _load():
    """Load from .pkl, training first if the file doesn't exist yet."""
    if not os.path.exists(MODEL_PATH):
        print("[Crop model] No saved model found — training now...")
        return _train_and_save()

    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)
    return bundle["model"], bundle["encoder"]


def predict_crop(inputs: dict) -> tuple[str, float]:
    """
    Given a dict with keys N, P, K, temperature, humidity, ph, rainfall,
    return (crop_name, confidence_float).

    Example:
        crop, conf = predict_crop({"N": 90, "P": 42, ..., "rainfall": 200})
        # → ("rice", 0.87)
    """
    clf, le = _load()

    # Build a 2-D array (1 sample × 7 features)
    X = np.array([[inputs[f] for f in FEATURES]])

    probs      = clf.predict_proba(X)[0]      # probability for each class
    top_idx    = int(np.argmax(probs))         # index of highest probability
    confidence = float(probs[top_idx])
    crop_name  = le.inverse_transform([top_idx])[0]

    return crop_name, confidence


# Quick sanity check — run: python ai/predictor.py
if __name__ == "__main__":
    _train_and_save()
    crop, conf = predict_crop({
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.8, "humidity": 82.0,
        "ph": 6.5, "rainfall": 202.9,
    })
    print(f"Test prediction → {crop}  ({conf:.1%})")
