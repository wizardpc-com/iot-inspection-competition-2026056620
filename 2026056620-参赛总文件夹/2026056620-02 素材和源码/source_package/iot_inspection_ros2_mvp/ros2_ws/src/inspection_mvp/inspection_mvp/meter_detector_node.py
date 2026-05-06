import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MeterDetectorNode(Node):
    """Run the YOLOv5 meter key-part model through a local detect.py entry."""

    def __init__(self):
        super().__init__("meter_detector_node")
        self.declare_parameter("meter_model_path", "../models/meter_best.pt")
        self.declare_parameter("meter_yolov5_detect_script", "../models/yolov5/detect.py")
        self.declare_parameter("meter_conf_threshold", 0.5)
        self.declare_parameter("meter_output_dir", "../outputs/meter_annotated")
        self.declare_parameter("meter_required_classes", ["base", "start", "end", "tip"])
        self.declare_parameter("meter_class_names", ["base", "start", "end", "tip"])
        self.declare_parameter("meter_min_value", 0.0)
        self.declare_parameter("meter_max_value", 100.0)
        self.declare_parameter("meter_unit", "unit")
        self.declare_parameter("meter_angle_direction", "clockwise")

        self.model_path = self._resolve_path(
            self.get_parameter("meter_model_path").get_parameter_value().string_value
        )
        self.detect_script = self._resolve_path(
            self.get_parameter("meter_yolov5_detect_script").get_parameter_value().string_value
        )
        self.conf_threshold = (
            self.get_parameter("meter_conf_threshold").get_parameter_value().double_value
        )
        self.output_dir = self._resolve_path(
            self.get_parameter("meter_output_dir").get_parameter_value().string_value
        )
        self.required_classes = list(
            self.get_parameter("meter_required_classes")
            .get_parameter_value()
            .string_array_value
        ) or ["base", "start", "end", "tip"]
        self.class_names = list(
            self.get_parameter("meter_class_names").get_parameter_value().string_array_value
        ) or ["base", "start", "end", "tip"]
        self.meter_min_value = (
            self.get_parameter("meter_min_value").get_parameter_value().double_value
        )
        self.meter_max_value = (
            self.get_parameter("meter_max_value").get_parameter_value().double_value
        )
        self.meter_unit = self.get_parameter("meter_unit").get_parameter_value().string_value
        self.angle_direction = (
            self.get_parameter("meter_angle_direction").get_parameter_value().string_value
            or "clockwise"
        ).lower()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.publisher = self.create_publisher(String, "/vision/meter_result", 10)
        self.subscription = self.create_subscription(
            String, "/inspection/image_path", self._on_image_path, 10
        )

        self.get_logger().info(
            "Meter detector ready. "
            f"backend=yolov5_detect_py, model_path={self.model_path}, "
            f"detect_script={self.detect_script}, conf_threshold={self.conf_threshold}, "
            f"output_dir={self.output_dir}"
        )
        self._log_backend_status()

    @staticmethod
    def _resolve_path(path_text):
        return Path(path_text).expanduser().resolve()

    def _log_backend_status(self):
        if not self.model_path.exists():
            self.get_logger().error(
                f"Meter model file not found: {self.model_path}. "
                "Put the YOLOv5 meter weight at models/meter_best.pt."
            )
        if not self.detect_script.exists():
            self.get_logger().error(
                f"YOLOv5 detect.py not found: {self.detect_script}. "
                "Put the YOLOv5 repository under models/yolov5/."
            )

    def _on_image_path(self, msg):
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().error(f"Invalid JSON on /inspection/image_path: {exc}")
            return

        station_id = payload.get("station_id", "UNKNOWN")
        image_path = self._resolve_path(payload.get("image_path", ""))
        self.get_logger().info(
            f"Meter image received. station_id={station_id}, image_path={image_path}"
        )

        if not image_path.exists():
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                annotated_save_ok=False,
                detections=[],
                meter_status="error",
                reason="image_not_found",
                error=f"Image file not found: {image_path}",
            )
            return

        if not self.model_path.exists() or not self.detect_script.exists():
            missing = []
            if not self.model_path.exists():
                missing.append(f"meter_model:{self.model_path}")
            if not self.detect_script.exists():
                missing.append(f"yolov5_detect_py:{self.detect_script}")
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                annotated_save_ok=False,
                detections=[],
                meter_status="error",
                reason="meter_yolov5_backend_unavailable",
                error="missing " + "; ".join(missing),
            )
            return

        try:
            run_dir = self._run_yolov5_detect(image_path)
            detections = self._parse_yolov5_labels(run_dir, image_path)
            annotated_image_path = self._find_annotated_image(run_dir, image_path)
            annotated_save_ok = bool(annotated_image_path and Path(annotated_image_path).exists())
            meter_status, reason = self._meter_status(detections)
            reading = self._estimate_reading(detections)
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path=annotated_image_path,
                annotated_save_ok=annotated_save_ok,
                detections=detections,
                meter_status=meter_status,
                reason=reason,
                error=None if annotated_save_ok else f"annotated_image_not_found:{run_dir}",
                reading=reading,
            )
        except Exception as exc:
            self.get_logger().error(f"YOLOv5 meter inference failed: {exc}")
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                annotated_save_ok=False,
                detections=[],
                meter_status="error",
                reason="yolov5_inference_failed",
                error=str(exc),
            )

    @staticmethod
    def _safe_stem(image_path):
        return "".join(
            char if char.isalnum() or char in {"-", "_"} else "_" for char in image_path.stem
        )[:80]

    def _run_yolov5_detect(self, image_path):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run_name = f"{self._safe_stem(image_path)}_{timestamp}_meter"
        command = [
            sys.executable,
            str(self.detect_script),
            "--weights",
            str(self.model_path),
            "--source",
            str(image_path),
            "--project",
            str(self.output_dir),
            "--name",
            run_name,
            "--exist-ok",
            "--save-txt",
            "--save-conf",
            "--conf-thres",
            str(self.conf_threshold),
        ]
        self.get_logger().info("Running YOLOv5 meter detect.py.")
        completed = subprocess.run(
            command,
            cwd=str(self.detect_script.parent),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if completed.returncode != 0:
            error = (
                f"returncode={completed.returncode}; "
                f"stderr={completed.stderr[-1200:]}; stdout={completed.stdout[-1200:]}"
            )
            raise RuntimeError(error)
        return self.output_dir / run_name

    def _class_name(self, class_id):
        if 0 <= class_id < len(self.class_names):
            return self.class_names[class_id]
        return f"class_{class_id}"

    def _parse_yolov5_labels(self, run_dir, image_path):
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"cv2_read_failed:{image_path}")
        height, width = image.shape[:2]
        label_path = run_dir / "labels" / f"{image_path.stem}.txt"
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
                    "class_name": self._class_name(class_id),
                }
            )
        return detections

    @staticmethod
    def _find_annotated_image(run_dir, image_path):
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

    @staticmethod
    def _class_counts(detections):
        counts = {}
        for item in detections:
            class_name = item.get("class_name", "unknown")
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts

    def _meter_status(self, detections):
        if not detections:
            return "needs_review", "no_meter_key_parts_detected"
        max_conf = max(item["conf"] for item in detections)
        if max_conf < self.conf_threshold:
            return "needs_review", "meter_key_part_confidence_below_threshold"
        counts = self._class_counts(detections)
        matched = sum(1 for class_name in self.required_classes if counts.get(class_name, 0) > 0)
        majority = (len(self.required_classes) // 2) + 1
        if matched >= majority:
            return (
                "structure_detected",
                f"detected_required_meter_parts={matched}/{len(self.required_classes)}",
            )
        return (
            "needs_review",
            f"insufficient_required_meter_parts={matched}/{len(self.required_classes)}",
        )

    @staticmethod
    def _bbox_center(detection):
        x1, y1, x2, y2 = detection["bbox"]
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def _best_detection_by_class(self, detections):
        best = {}
        for item in detections:
            class_name = item.get("class_name", "")
            if class_name not in best or item.get("conf", 0.0) > best[class_name].get("conf", 0.0):
                best[class_name] = item
        return best

    @staticmethod
    def _angle_degrees(origin, point):
        dx = point[0] - origin[0]
        dy = origin[1] - point[1]
        return math.degrees(math.atan2(dy, dx)) % 360.0

    @staticmethod
    def _angular_delta(start_angle, end_angle, direction):
        if direction == "counterclockwise":
            return (end_angle - start_angle) % 360.0
        return (start_angle - end_angle) % 360.0

    @staticmethod
    def _clamp(value, lower, upper):
        return max(lower, min(upper, value))

    def _estimate_reading(self, detections):
        best = self._best_detection_by_class(detections)
        missing = [name for name in ["base", "start", "end", "tip"] if name not in best]
        if missing:
            return {
                "reading_status": "needs_key_parts",
                "reading_value": None,
                "reading_unit": self.meter_unit,
                "reading_ratio": None,
                "reading_method": "keypart_angle_linear_scale",
                "reading_reason": "missing_key_parts=" + ",".join(missing),
            }

        base = self._bbox_center(best["base"])
        start_angle = self._angle_degrees(base, self._bbox_center(best["start"]))
        end_angle = self._angle_degrees(base, self._bbox_center(best["end"]))
        tip_angle = self._angle_degrees(base, self._bbox_center(best["tip"]))
        span = self._angular_delta(start_angle, end_angle, self.angle_direction)
        pointer_delta = self._angular_delta(start_angle, tip_angle, self.angle_direction)

        if span < 1.0:
            return {
                "reading_status": "needs_review",
                "reading_value": None,
                "reading_unit": self.meter_unit,
                "reading_ratio": None,
                "reading_method": "keypart_angle_linear_scale",
                "reading_reason": "invalid_scale_angle_span",
            }

        ratio = self._clamp(pointer_delta / span, 0.0, 1.0)
        reading_value = self.meter_min_value + ratio * (
            self.meter_max_value - self.meter_min_value
        )
        return {
            "reading_status": "estimated",
            "reading_value": round(reading_value, 4),
            "reading_unit": self.meter_unit,
            "reading_ratio": round(ratio, 4),
            "reading_method": "keypart_angle_linear_scale",
            "reading_reason": (
                f"start_angle={start_angle:.2f},end_angle={end_angle:.2f},"
                f"tip_angle={tip_angle:.2f},direction={self.angle_direction}"
            ),
        }

    def _publish_result(
        self,
        station_id,
        image_path,
        annotated_image_path,
        annotated_save_ok,
        detections,
        meter_status,
        reason,
        error,
        reading=None,
    ):
        class_counts = self._class_counts(detections)
        max_conf = max((item["conf"] for item in detections), default=0.0)
        if reading is None:
            reading = {
                "reading_status": "error" if meter_status == "error" else "needs_key_parts",
                "reading_value": None,
                "reading_unit": self.meter_unit,
                "reading_ratio": None,
                "reading_method": "keypart_angle_linear_scale",
                "reading_reason": reason,
            }

        payload = {
            "station_id": station_id,
            "image_path": str(image_path),
            "annotated_image_path": annotated_image_path,
            "annotated_save_ok": annotated_save_ok,
            "meter_output_dir": str(self.output_dir),
            "detected": bool(detections),
            "detector_type": "meter_keypart_detector",
            "model_backend": "yolov5_detect_py",
            "count": len(detections),
            "class_counts": class_counts,
            "max_conf": round(max_conf, 4),
            "detections": detections,
            "meter_status": meter_status,
            "reading_status": reading["reading_status"],
            "reading_value": reading["reading_value"],
            "reading_unit": reading["reading_unit"],
            "reading_ratio": reading["reading_ratio"],
            "reading_method": reading["reading_method"],
            "reading_reason": reading["reading_reason"],
            "reason": reason,
            "threshold": self.conf_threshold,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error,
        }
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.publisher.publish(msg)
        self.get_logger().info(
            f"Published meter result. station_id={station_id}, "
            f"meter_status={meter_status}, count={len(detections)}, "
            f"max_conf={max_conf:.4f}, reading_status={reading['reading_status']}, "
            f"reading_value={reading['reading_value']}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = MeterDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Meter detector interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
