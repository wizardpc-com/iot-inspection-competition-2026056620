from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    ROOT / "models" / "meter_best.pt",
    ROOT / "models" / "yolov5" / "detect.py",
    ROOT / "outputs" / "meter_annotated",
]


def main():
    ok = True
    print("Meter YOLOv5 asset check")
    for path in REQUIRED:
        exists = path.exists()
        print(f"[{'OK' if exists else 'MISSING'}] {path}")
        ok = ok and exists

    if not (ROOT / "models" / "yolov5" / "detect.py").exists():
        print()
        print("Put the YOLOv5 repository under:")
        print(ROOT / "models" / "yolov5")
        print()
        print("Expected command used by ROS2 meter node:")
        print(
            "python3 models/yolov5/detect.py "
            "--weights models/meter_best.pt --source <image> --save-txt --save-conf"
        )

    if not ok:
        raise SystemExit("Missing required meter YOLOv5 assets.")
    print("Meter YOLOv5 assets are ready.")


if __name__ == "__main__":
    main()
