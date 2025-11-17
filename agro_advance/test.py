import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import json
from disease_remedies import REMEDIES

# load model & labels
model = tf.keras.models.load_model("disease_model.h5")
class_labels = json.load(open("class_labels.json"))

# image path
img_path="test.jpg.JPG"  # 👈 path to any test image
img = image.load_img(img_path, target_size=(128,128))
img_array = image.img_to_array(img)/255.0
img_array = np.expand_dims(img_array, axis=0)

# predict
pred = model.predict(img_array)
pred_class = class_labels[np.argmax(pred)]
confidence = np.max(pred)

print(f"Predicted: {pred_class} ({confidence*100:.2f}% confidence)")
if pred_class in REMEDIES:
    print("Description:", REMEDIES[pred_class]["description"])
    print("Remedy:", REMEDIES[pred_class]["remedy"])
else:
    print("No remedy found for this disease.")