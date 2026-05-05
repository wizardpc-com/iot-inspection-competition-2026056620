import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import cv2


def class_name(model, class_id):
    names = getattr(model, "names", {})
    if isinstance(names, dict):
        return str(names.get(class_id, f"class_{class_id}"))
    if isinstance(names, list) and 0 <= class_id < len(names):
        return str(names[class_id])
    return f"class_{class_id}"


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
    parser = argparse.ArgumentParser(description="Standalone meter key-part model smoke test.")
    parser.add_argument("--model", default="models/meter_best.pt", help="Path to meter model.")
    parser.add_argument("--image", required=True, help="Path to test image.")
    parser.add_argument("--conf", type=float, default=0.5, help="Confidence threshold.")
    parser.add_argument("--min-value", type=float, default=0.0, help="Meter minimum value.")
    parser.add_argument("--max-value", type=float, default=100.0, help="Meter maximum value.")
    parser.add_argument("--unit", default="unit", help="Meter unit label.")
    parser.add_argument(
        "--direction",
        default="clockwise",
        choices=["clockwise", "counterclockwise"],
        help="Scale angle direction from start to end.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/meter_annotated",
        help="Directory for annotated test output.",
    )
    args = parser.parse_args()

    model_path = Path(args.model).expanduser().resolve()
    image_path = Path(args.image).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not model_path.exists():
        raise SystemExit(f"Meter model not found: {model_path}")
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    from ultralytics import YOLO

    model = YOLO(str(model_path))
    results = model.predict(source=str(image_path), conf=args.conf, save=False, show=False)
    result = results[0]

    detections = []
    boxes = getattr(result, "boxes", None)
    if boxes is not None:
        for box in boxes:
            conf = float(box.conf[0].item()) if box.conf is not None else 0.0
            class_id = int(box.cls[0].item()) if box.cls is not None else 0
            xyxy = box.xyxy[0].detach().cpu().tolist()
            detections.append(
                {
                    "bbox": [round(float(value), 2) for value in xyxy],
                    "conf": round(conf, 4),
                    "class_id": class_id,
                    "class_name": class_name(model, class_id),
                }
            )

    output_path = output_dir / f"{image_path.stem}_meter_test.jpg"
    cv2.imwrite(str(output_path), result.plot())
    reading = estimate_reading(
        detections,
        min_value=args.min_value,
        max_value=args.max_value,
        unit=args.unit,
        direction=args.direction,
    )

    payload = {
        "image_path": str(image_path),
        "annotated_image_path": str(output_path),
        "detector_type": "meter_keypoint_detector",
        "model_backend": "ultralytics",
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
