import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================
# DATASET PATH
# ======================
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "dataset")

IMG_SIZE = (128, 128)
BATCH_SIZE = 32

# ======================
# LOAD DATA
# ======================
train_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(DATA_DIR, "train"),
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary"
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(DATA_DIR, "valid"),
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary"
)

# ======================
# NORMALIZATION
# ======================
normalization_layer = tf.keras.layers.Rescaling(1./255)

train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

# ======================
# PREFETCH
# ======================
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

# ======================
# CNN MODEL
# ======================
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(128,128,3)),
    layers.MaxPooling2D(),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(),

    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')
])

# ======================
# COMPILE MODEL
# ======================
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# ======================
# TRAIN MODEL
# ======================
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

# ======================
# SAVE MODEL
# ======================
out_path = os.path.join(SCRIPT_DIR, "weed_crop_model.h5")
model.save(out_path)

print(f"✅ Model saved as {out_path}")

# ======================
# PLOT ACCURACY
# ======================
plt.plot(history.history['accuracy'], label='train accuracy')
plt.plot(history.history['val_accuracy'], label='val accuracy')
plt.legend()
plt.title("Model Accuracy")
plt.show()