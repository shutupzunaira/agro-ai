import os
import pickle
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_model.pkl")

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def _load():
    if not os.path.exists(MODEL_PATH):
        raise Exception("Model not found. Train first.")

    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)

    return bundle["model"], bundle["encoder"]


def predict_crop(inputs: dict):
    model, le = _load()

    X = np.array([[inputs[f] for f in FEATURES]])

    probs = model.predict_proba(X)[0]
    idx = int(np.argmax(probs))

    confidence = float(probs[idx])
    crop_name = le.inverse_transform([idx])[0]

    return crop_name, confidence