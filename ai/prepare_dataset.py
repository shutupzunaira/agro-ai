import os
import shutil

BASE_DIR = "dataset"

# class mapping from YOLO labels
CLASS_NAMES = ["crop", "weed"]

def create_dirs():
    for split in ["train", "valid"]:
        for cls in CLASS_NAMES:
            os.makedirs(f"{BASE_DIR}/{split}/{cls}", exist_ok=True)

def process_split(split):
    images_path = f"{BASE_DIR}/{split}/images"
    labels_path = f"{BASE_DIR}/{split}/labels"

    for file in os.listdir(images_path):
        if not file.endswith(".jpg"):
            continue

        img_path = os.path.join(images_path, file)
        label_file = file.replace(".jpg", ".txt")
        label_path = os.path.join(labels_path, label_file)

        if not os.path.exists(label_path):
            continue

        with open(label_path, "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            continue

        # take first object class
        class_id = int(lines[0].split()[0])
        class_name = CLASS_NAMES[class_id]

        dest_path = f"{BASE_DIR}/{split}/{class_name}/{file}"
        shutil.copy(img_path, dest_path)

def main():
    create_dirs()
    process_split("train")
    process_split("valid")
    print("✅ Dataset prepared for CNN!")

if __name__ == "__main__":
    main()