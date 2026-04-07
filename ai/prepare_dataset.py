import os
import shutil
import random

# =========================
# PATH CONFIG
# =========================
SOURCE_DIR = "/Users/shambhavisinha/Downloads/plant_seedlings_v2/nonsegmentedv2"
BASE_DIR = "dataset"

# =========================
# CLASS MAPPING
# =========================
WEED_CLASSES = [
    "Black-grass",
    "Charlock",
    "Cleavers",
    "Common Chickweed",
    "Fat Hen",
    "Loose Silky-bent",
    "Scentless Mayweed",
    "Small-flowered Cranesbill"
]

CROP_CLASSES = [
    "Maize",
    "Common wheat",
    "Sugar beet"
]

# =========================
# CREATE FOLDERS
# =========================
def create_dirs():
    for split in ["train", "valid"]:
        for cls in ["weed", "crop"]:
            os.makedirs(f"{BASE_DIR}/{split}/{cls}", exist_ok=True)

# =========================
# PROCESS EACH CLASS
# =========================
def process_class(class_name, label):
    class_path = os.path.join(SOURCE_DIR, class_name)

    if not os.path.exists(class_path):
        print(f"⚠️ Skipping missing folder: {class_name}")
        return

    images = [
        f for f in os.listdir(class_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if len(images) == 0:
        print(f"⚠️ No images found in: {class_name}")
        return

    random.shuffle(images)

    split_idx = int(0.8 * len(images))

    train_imgs = images[:split_idx]
    val_imgs = images[split_idx:]

    # Copy train images
    for img in train_imgs:
        src = os.path.join(class_path, img)
        dst = os.path.join(BASE_DIR, "train", label, img)
        shutil.copy2(src, dst)

    # Copy validation images
    for img in val_imgs:
        src = os.path.join(class_path, img)
        dst = os.path.join(BASE_DIR, "valid", label, img)
        shutil.copy2(src, dst)

    print(f"✔ Processed {class_name} -> {label}")

# =========================
# MAIN FUNCTION
# =========================
def main():
    print("🚀 Starting dataset preparation...")

    create_dirs()

    # Process weed classes
    for cls in WEED_CLASSES:
        process_class(cls, "weed")

    # Process crop classes
    for cls in CROP_CLASSES:
        process_class(cls, "crop")

    print("\n✅ Dataset successfully prepared!")
    print(f"📁 Output folder: {BASE_DIR}/")

# =========================
# RUN SCRIPT
# =========================
if __name__ == "__main__":
    main()