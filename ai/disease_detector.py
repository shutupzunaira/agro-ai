"""
ai/disease_detector.py — Crop disease detection from leaf images.

CURRENT APPROACH (demo / local):
  We use a rule-based colour analysis of the uploaded image to simulate
  a disease detector. This works immediately with zero extra dependencies.

UPGRADE PATH (production):
  Replace the body of detect_disease() with a call to a real CNN model,
  for example:
    - A PyTorch model trained on the PlantVillage dataset
    - The Roboflow plant-disease API
    - A TensorFlow/Keras .h5 model loaded with tf.keras.models.load_model()

  Example PyTorch swap-in (once you have a model file):
    import torch
    from torchvision import transforms
    from PIL import Image

    model = torch.load("ai/plant_disease_model.pth")
    model.eval()

    img = Image.open(image_path).convert("RGB")
    tensor = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])(img).unsqueeze(0)

    with torch.no_grad():
        logits = model(tensor)
        probs  = torch.softmax(logits, dim=1)[0]
    ...
"""

import os

# Disease knowledge base: name → treatment advice
DISEASE_TREATMENTS = {
    "Healthy":                 "No treatment needed. Continue monitoring.",
    "Leaf Blight":             "Apply copper-based fungicide. Remove affected leaves. Improve air circulation.",
    "Powdery Mildew":          "Spray with diluted neem oil or potassium bicarbonate solution. Reduce leaf wetness.",
    "Bacterial Leaf Spot":     "Use copper hydroxide spray. Avoid overhead irrigation. Rotate crops annually.",
    "Early Blight":            "Apply chlorothalonil fungicide. Remove lower infected leaves. Mulch around plants.",
    "Late Blight":             "Urgent: apply mancozeb fungicide. Remove and destroy all infected material immediately.",
    "Rust":                    "Apply triazole fungicide at first sign. Improve field drainage. Use resistant varieties.",
    "Mosaic Virus":            "No chemical cure. Remove infected plants to prevent spread. Control aphid vectors.",
    "Nutrient Deficiency":     "Conduct a full soil test. Apply balanced NPK fertiliser based on results.",
}


def _analyse_image_colours(image_path: str) -> str:
    """
    Simplified colour-histogram analysis to simulate disease classification.

    Real models use CNNs trained on thousands of labelled images.
    This stub gives the app a working result while you set up a real model.
    """
    try:
        # pillow (PIL) reads image files and lets us access pixel data
        from PIL import Image
        import numpy as np

        img    = Image.open(image_path).convert("RGB").resize((100, 100))
        pixels = np.array(img).reshape(-1, 3).astype(float)

        avg_r = pixels[:, 0].mean()   # average red channel
        avg_g = pixels[:, 1].mean()   # average green channel
        avg_b = pixels[:, 2].mean()   # average blue channel

        # Heuristic rules (very simplified — replace with real model)
        if avg_g > 90 and avg_r < 100:
            return "Healthy"
        elif avg_r > 130 and avg_g < 90:
            return "Rust"
        elif avg_r > 110 and avg_g > 100 and avg_b < 80:
            return "Early Blight"
        elif avg_r > 140 and avg_g < 80:
            return "Late Blight"
        elif avg_r < 80 and avg_g < 80 and avg_b < 80:
            return "Bacterial Leaf Spot"
        elif avg_g < 70 and avg_r < 70:
            return "Mosaic Virus"
        elif avg_b > avg_g and avg_b > avg_r:
            return "Powdery Mildew"
        else:
            return "Leaf Blight"

    except Exception as e:
        print(f"[Disease detector] Image read error: {e}")
        return "Nutrient Deficiency"


def detect_disease(image_path: str) -> tuple[str, float, str]:
    """
    Analyse an uploaded leaf image and return:
      (disease_name, confidence, treatment_advice)

    Swap out _analyse_image_colours() with a real CNN call to improve accuracy.
    """
    import random

    disease_name = _analyse_image_colours(image_path)

    # Simulated confidence: real model would return softmax probabilities
    confidence = round(random.uniform(0.72, 0.96), 3)

    treatment = DISEASE_TREATMENTS.get(disease_name, "Consult an agronomist.")

    return disease_name, confidence, treatment
