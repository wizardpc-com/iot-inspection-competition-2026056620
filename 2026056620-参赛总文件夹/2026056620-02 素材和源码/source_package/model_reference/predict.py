import os
from ultralytics import YOLO


model_path = "best.pt"
model = YOLO(model_path)

image_folder = "demo_images"
image_paths = [
    os.path.join(image_folder, "picture_1.jpg"),
    os.path.join(image_folder, "picture_2.jpg"),
]

existing_images = [path for path in image_paths if os.path.exists(path)]
if not existing_images:
    print("No demo images found. Please check demo_images/.")
else:
    model.predict(source=existing_images, save=True, show=True, conf=0.5)
