import os
import pickle
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_model.pkl")

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def _build_sample_dataset():
    rows = [
        [90, 42, 43, 20.8, 82.0, 6.5, 202.9, "rice"],
        [85, 58, 41, 21.7, 80.3, 7.0, 226.6, "rice"],
        [60, 55, 44, 23.0, 82.3, 7.8, 263.9, "maize"],
        [74, 35, 40, 26.5, 80.0, 6.9, 85.4, "maize"],
        [20, 30, 10, 25.0, 58.5, 5.8, 72.0, "wheat"],
        [22, 28, 12, 27.0, 56.0, 5.5, 68.0, "wheat"],
        [14, 12, 14, 27.0, 54.0, 6.9, 40.0, "cotton"],
        [15, 11, 13, 28.5, 55.0, 7.0, 45.0, "cotton"],
        [50, 53, 48, 27.0, 66.0, 6.0, 140.0, "sugarcane"],
        [52, 55, 50, 26.5, 68.0, 6.1, 135.0, "sugarcane"],
    ]

    X = np.array([r[:7] for r in rows])
    labels = [r[7] for r in rows]
    return X, labels


def _train_and_save():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder

    X, labels = _build_sample_dataset()

    le = LabelEncoder()
    y = le.fit_transform(labels)

    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": clf, "encoder": le}, f)

    print(f"[Crop model] Saved → {MODEL_PATH}")
    return clf, le


def _load():
    if not os.path.exists(MODEL_PATH):
        return _train_and_save()

    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)

    return bundle["model"], bundle["encoder"]


def predict_crop(inputs: dict):
    clf, le = _load()

    X = np.array([[inputs[f] for f in FEATURES]])

    probs = clf.predict_proba(X)[0]
    top_idx = int(np.argmax(probs))

    confidence = float(probs[top_idx])
    crop_name = le.inverse_transform([top_idx])[0]

    return crop_name, confidence


if __name__ == "__main__":
    _train_and_save()

    crop, conf = predict_crop({
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.8, "humidity": 82.0,
        "ph": 6.5, "rainfall": 202.9,
    })

    print(f"Test → {crop} ({conf:.1%})")