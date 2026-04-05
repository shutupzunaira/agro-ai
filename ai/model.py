import numpy as np
from PIL import Image
import tensorflow as tf

# Load model
model = tf.keras.models.load_model("ai/weed_crop_model.h5")


def predict_weed_or_crop(image_path):
    try:
        img = Image.open(image_path)

        # Ensure RGB
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Preprocess
        img = img.resize((224, 224))
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)

        # Prediction
        prediction = model.predict(img)

        # -----------------------------
        # CASE 1: Binary sigmoid model
        # -----------------------------
        if prediction.shape[-1] == 1:
            prob_weed = float(prediction[0][0])
            prob_crop = 1 - prob_weed

        # -----------------------------
        # CASE 2: Softmax model (2-class)
        # -----------------------------
        else:
            prob_crop = float(prediction[0][0])
            prob_weed = float(prediction[0][1])

        confidence = max(prob_weed, prob_crop)

        # -----------------------------
        # FIXED LOGIC RULES
        # -----------------------------

        # Invalid image (too low confidence)
        if confidence < 0.5:
            return {
                "label": "Invalid Image ❌",
                "confidence": confidence,
                "suggestion": "Upload a clearer plant image."
            }

        # Weed detected
        if prob_weed > prob_crop:
            return {
                "label": "Weed Detected 🌱",
                "confidence": confidence,
                "suggestion": "Remove manually or use targeted herbicide."
            }

        # Crop detected
        else:
            return {
                "label": "Crop Detected 🌾",
                "confidence": confidence,
                "suggestion": "Healthy crop. Continue normal care."
            }

    except Exception as e:
        print("Error:", e)
        return {
            "label": "Error ❌",
            "confidence": 0.0,
            "suggestion": "Something went wrong."
        }