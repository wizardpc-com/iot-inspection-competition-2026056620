import argparse
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2


def safe_stem(image_path):
    return "".join(
        char if char.isalnum() or char in {"-", "_"} else "_" for char in image_path.stem
    )[:80]


def class_name(class_names, class_id):
    if 0 <= class_id < len(class_names):
        return class_names[class_id]
    return f"class_{class_id}"


def parse_labels(label_path, image_path, class_names):
    image = cv2.imread(str(image_path))
    if image is None:
        raise SystemExit(f"cv2 failed to read image: {image_path}")
    height, width = image.shape[:2]
    if not label_path.exists():
        return []

    detections = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        class_id = int(float(parts[0]))
        x_center = float(parts[1]) * width
        y_center = float(parts[2]) * height
        box_width = float(parts[3]) * width
        box_height = float(parts[4]) * height
        conf = float(parts[5]) if len(parts) >= 6 else 0.0
        detections.append(
            {
                "bbox": [
                    round(x_center - box_width / 2.0, 2),
                    round(y_center - box_height / 2.0, 2),
                    round(x_center + box_width / 2.0, 2),
                    round(y_center + box_height / 2.0, 2),
                ],
                "conf": round(conf, 4),
                "class_id": class_id,
                "class_name": class_name(class_names, class_id),
            }
        )
    return detections


def find_annotated_image(run_dir, image_path):
    candidates = [
        run_dir / image_path.name,
        run_dir / f"{image_path.stem}.jpg",
        run_dir / f"{image_path.stem}.jpeg",
        run_dir / f"{image_path.stem}.png",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())
    for candidate in sorted(run_dir.glob(f"{image_path.stem}.*")):
        if candidate.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            return str(candidate.resolve())
    return ""


def center(detection):
    x1, y1, x2, y2 = detection["bbox"]
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def angle_degrees(origin, point):
    dx = point[0] - origin[0]
    dy = origin[1] - point[1]
    return math.degrees(math.atan2(dy, dx)) % 360.0


def angular_delta(start_angle, end_angle, direction):
    if direction == "counterclockwise":
        return (end_angle - start_angle) % 360.0
    return (start_angle - end_angle) % 360.0


def estimate_reading(detections, min_value, max_value, unit, direction):
    best = {}
    for item in detections:
        name = item["class_name"]
        if name not in best or item["conf"] > best[name]["conf"]:
            best[name] = item
    missing = [name for name in ["base", "start", "end", "tip"] if name not in best]
    if missing:
        return {
            "reading_status": "needs_key_parts",
            "reading_value": None,
            "reading_unit": unit,
            "reading_ratio": None,
            "reading_method": "keypart_angle_linear_scale",
            "reading_reason": "missing_key_parts=" + ",".join(missing),
        }

    base = center(best["base"])
    start_angle = angle_degrees(base, center(best["start"]))
    end_angle = angle_degrees(base, center(best["end"]))
    tip_angle = angle_degrees(base, center(best["tip"]))
    span = angular_delta(start_angle, end_angle, direction)
    pointer_delta = angular_delta(start_angle, tip_angle, direction)
    if span < 1.0:
        return {
            "reading_status": "needs_review",
            "reading_value": None,
            "reading_unit": unit,
            "reading_ratio": None,
            "reading_method": "keypart_angle_linear_scale",
            "reading_reason": "invalid_scale_angle_span",
        }
    ratio = max(0.0, min(1.0, pointer_delta / span))
    return {
        "reading_status": "estimated",
        "reading_value": round(min_value + ratio * (max_value - min_value), 4),
        "reading_unit": unit,
        "reading_ratio": round(ratio, 4),
        "reading_method": "keypart_angle_linear_scale",
        "reading_reason": (
            f"start_angle={start_angle:.2f},end_angle={end_angle:.2f},"
            f"tip_angle={tip_angle:.2f},direction={direction}"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Standalone YOLOv5 meter model smoke test.")
    parser.add_argument("--model", default="models/meter_best.pt", help="Path to meter model.")
    parser.add_argument("--detect-script", default="models/yolov5/detect.py")
    parser.add_argument("--image", required=True, help="Path to test image.")
    parser.add_argument("--conf", type=float, default=0.5, help="Confidence threshold.")
    parser.add_argument("--class-names", default="base,start,end,tip")
    parser.add_argument("--min-value", type=float, default=0.0, help="Meter minimum value.")
    parser.add_argument("--max-value", type=float, default=100.0, help="Meter maximum value.")
    parser.add_argument("--unit", default="unit", help="Meter unit label.")
    parser.add_argument(
        "--direction",
        default="clockwise",
        choices=["clockwise", "counterclockwise"],
        help="Scale angle direction from start to end.",
    )
    parser.add_argument("--output-dir", default="outputs/meter_annotated")
    args = parser.parse_args()

    model_path = Path(args.model).expanduser().resolve()
    detect_script = Path(args.detect_script).expanduser().resolve()
    image_path = Path(args.image).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not model_path.exists():
        raise SystemExit(f"Meter model not found: {model_path}")
    if not detect_script.exists():
        raise SystemExit(f"YOLOv5 detect.py not found: {detect_script}")
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_name = f"{safe_stem(image_path)}_{timestamp}_meter_test"
    command = [
        sys.executable,
        str(detect_script),
        "--weights",
        str(model_path),
        "--source",
        str(image_path),
        "--project",
        str(output_dir),
        "--name",
        run_name,
        "--exist-ok",
        "--save-txt",
        "--save-conf",
        "--conf-thres",
        str(args.conf),
    ]
    completed = subprocess.run(
        command,
        cwd=str(detect_script.parent),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"YOLOv5 detect.py failed: returncode={completed.returncode}\n"
            f"stderr={completed.stderr[-2000:]}\nstdout={completed.stdout[-2000:]}"
        )

    run_dir = output_dir / run_name
    class_names = [item.strip() for item in args.class_names.split(",") if item.strip()]
    detections = parse_labels(run_dir / "labels" / f"{image_path.stem}.txt", image_path, class_names)
    reading = estimate_reading(
        detections,
        min_value=args.min_value,
        max_value=args.max_value,
        unit=args.unit,
        direction=args.direction,
    )
    payload = {
        "image_path": str(image_path),
        "annotated_image_path": find_annotated_image(run_dir, image_path),
        "detector_type": "meter_keypart_detector",
        "model_backend": "yolov5_detect_py",
        "count": len(detections),
        "max_conf": max((item["conf"] for item in detections), default=0.0),
        "detections": detections,
        "reading_status": reading["reading_status"],
        "reading_value": reading["reading_value"],
        "reading_unit": reading["reading_unit"],
        "reading_ratio": reading["reading_ratio"],
        "reading_method": reading["reading_method"],
        "reading_reason": reading["reading_reason"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
