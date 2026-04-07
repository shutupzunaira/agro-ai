import os
import numpy as np

# Must match ai/train_model.py (IMG_SIZE and class folders crop / weed)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "weed_crop_model.h5")
WEED_IMG_SIZE = (128, 128)

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            import tensorflow as tf  # lazy: optional until weed detection runs
        except ImportError as e:
            raise ImportError(
                "TensorFlow is required for weed detection. Install with: pip install tensorflow"
            ) from e

        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(
                f"Missing CNN weights: place your trained file at {MODEL_PATH} "
                "(run ai/train_model.py or copy weed_crop_model.h5 into the ai/ folder)."
            )
        _model = tf.keras.models.load_model(MODEL_PATH)
    return _model


def predict_weed_or_crop(image_array):
    """
    image_array: float32 RGB, shape (H, W, 3), values in [0, 1].
    Trained with Keras binary labels: 0=crop, 1=weed (alphabetical folder order).
    """
    model = _get_model()

    img = np.expand_dims(image_array.astype(np.float32), axis=0)
    predictions = model.predict(img, verbose=0)

    # Sigmoid: single output = P(weed) when using binary_crossentropy with weed as class 1
    if predictions.shape[-1] == 1:
        prob_weed = float(predictions[0][0])
        if prob_weed > 0.5:
            return "weed", prob_weed
        return "crop", 1.0 - prob_weed

    # Softmax fallback (two outputs, order crop then weed)
    probs = predictions[0]
    idx = int(np.argmax(probs))
    confidence = float(probs[idx])
    return ("crop", "weed")[idx], confidence
