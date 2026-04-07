import os
import shutil

# Paths
image_dir = "dataset/test/images"
label_dir = "dataset/test/labels"

crop_dir = "dataset/test/crop"
weed_dir = "dataset/test/weed"

# Create folders
os.makedirs(crop_dir, exist_ok=True)
os.makedirs(weed_dir, exist_ok=True)

# Loop through labels
for file in os.listdir(label_dir):
    if file.endswith(".txt"):
        label_path = os.path.join(label_dir, file)

        with open(label_path, "r") as f:
            content = f.readline().strip()
            if not content:
                continue
            class_id = content.split()[0]

        # Change extension if needed (.png instead of .jpg)
        image_name = file.replace(".txt", ".jpg")
        image_path = os.path.join(image_dir, image_name)

        if os.path.exists(image_path):
            if class_id == "0":
                shutil.copy(image_path, crop_dir)
            else:
                shutil.copy(image_path, weed_dir)

print("✅ Conversion DONE")
