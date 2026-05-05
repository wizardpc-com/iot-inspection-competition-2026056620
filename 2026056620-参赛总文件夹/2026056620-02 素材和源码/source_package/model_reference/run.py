import glob
import os
from ultralytics import YOLO


root_path = os.environ.get("PIPE_INSPECTION_DATASET_ROOT", "<dataset_root>")
dataset_path = os.path.join(root_path, "pipe-crack-detection.v1i.yolov8")

label_files = glob.glob(os.path.join(dataset_path, "**", "*.txt"), recursive=True)
for file_path in label_files:
    if os.path.basename(file_path) in ["classes.txt", "notes.txt", "data.yaml"]:
        continue
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    with open(file_path, "w", encoding="utf-8") as file:
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                parts[0] = "0"
                file.write(" ".join(parts) + "\n")

yaml_path = os.path.join(dataset_path, "data.yaml")
fixed_path = dataset_path.replace("\\", "/")
new_yaml = f"""
path: {fixed_path}
train: train/images
val: valid/images
test: test/images

nc: 1
names: ['pipe_crack']
"""

with open(yaml_path, "w", encoding="utf-8") as file:
    file.write(new_yaml.strip())

if __name__ == "__main__":
    model = YOLO("yolov8n.pt")
    model.train(
        data=yaml_path,
        epochs=50,
        imgsz=640,
        batch=32,
        device=0,
        workers=0,
        name="Pipe_Final_Fix",
    )
