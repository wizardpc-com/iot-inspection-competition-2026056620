import json
import math
from datetime import datetime, timezone
from pathlib import Path

import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MeterDetectorNode(Node):
    """Detect meter key parts and publish structured ROS2 JSON results."""

    def __init__(self):
        super().__init__("meter_detector_node")
        self.declare_parameter("use_meter_stub", False)
        self.declare_parameter("meter_model_path", "../models/meter_best.pt")
        self.declare_parameter("meter_last_model_path", "../models/meter_last.pt")
        self.declare_parameter("meter_conf_threshold", 0.5)
        self.declare_parameter("meter_output_dir", "../outputs/meter_annotated")
        self.declare_parameter("meter_required_classes", ["base", "start", "end", "tip"])
        self.declare_parameter("meter_min_value", 0.0)
        self.declare_parameter("meter_max_value", 100.0)
        self.declare_parameter("meter_unit", "unit")
        self.declare_parameter("meter_angle_direction", "clockwise")

        self.model_path = self._resolve_path(
            self.get_parameter("meter_model_path").get_parameter_value().string_value
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
        )
        if not self.required_classes:
            self.required_classes = ["base", "start", "end", "tip"]
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
        self.model = None
        self.model_backend = "error"
        self._load_model_once()

        self.publisher = self.create_publisher(String, "/vision/meter_result", 10)
        self.subscription = self.create_subscription(
            String, "/inspection/image_path", self._on_image_path, 10
        )

        self.get_logger().info(
            "Meter detector ready. "
            f"model_path={self.model_path}, conf_threshold={self.conf_threshold}, "
            f"required_classes={self.required_classes}, output_dir={self.output_dir}"
        )

    @staticmethod
    def _resolve_path(path_text):
        return Path(path_text).expanduser().resolve()

    def _load_model_once(self):
        if not self.model_path.exists():
            self.get_logger().error(
                f"Meter model file not found: {self.model_path}. "
                "Put meter_best.pt under models/ or launch with use_meter_stub:=true."
            )
            self.model_backend = "error"
            return

        try:
            from ultralytics import YOLO

            self.model = YOLO(str(self.model_path))
            self.model_backend = "ultralytics"
            self.get_logger().info("Meter key-part model loaded with ultralytics.")
        except Exception as exc:
            self.model = None
            self.model_backend = "fallback"
            self.get_logger().error(
                "Meter model could not be loaded by ultralytics. "
                f"Publishing non-crashing error results. error={exc}"
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
            f"Received meter inspection image. station_id={station_id}, image_path={image_path}"
        )

        if not image_path.exists():
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                detections=[],
                meter_status="error",
                reason="image_not_found",
                error=f"Image file not found: {image_path}",
            )
            return

        if self.model is None:
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                detections=[],
                meter_status="error",
                reason="meter_model_unavailable",
                error=f"Meter model unavailable: {self.model_path}",
            )
            return

        try:
            results = self.model.predict(
                source=str(image_path),
                conf=self.conf_threshold,
                save=False,
                show=False,
                verbose=False,
            )
            result = results[0]
            detections = self._extract_detections(result)
            annotated_image_path = self._save_annotated_image(result, image_path)
            meter_status, reason = self._meter_status(detections)
            reading = self._estimate_reading(detections)
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path=annotated_image_path,
                detections=detections,
                meter_status=meter_status,
                reason=reason,
                error=None,
                reading=reading,
            )
        except Exception as exc:
            self.get_logger().error(f"Meter key-part inference failed: {exc}")
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                detections=[],
                meter_status="error",
                reason="inference_failed",
                error=str(exc),
            )

    def _class_name(self, class_id):
        names = getattr(self.model, "names", {}) if self.model is not None else {}
        if isinstance(names, dict):
            return str(names.get(class_id, f"class_{class_id}"))
        if isinstance(names, list) and 0 <= class_id < len(names):
            return str(names[class_id])
        return f"class_{class_id}"

    def _extract_detections(self, result):
        detections = []
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        for box in boxes:
            conf = float(box.conf[0].item()) if box.conf is not None else 0.0
            class_id = int(box.cls[0].item()) if box.cls is not None else 0
            xyxy = box.xyxy[0].detach().cpu().tolist()
            detections.append(
                {
                    "bbox": [round(float(value), 2) for value in xyxy],
                    "conf": round(conf, 4),
                    "class_id": class_id,
                    "class_name": self._class_name(class_id),
                }
            )
        return detections

    def _save_annotated_image(self, result, image_path):
        annotated = result.plot()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        output_path = self.output_dir / f"{image_path.stem}_{timestamp}_meter.jpg"
        cv2.imwrite(str(output_path), annotated)
        self.get_logger().info(f"Meter annotated result saved: {output_path}")
        return str(output_path.resolve())

    def _class_counts(self, detections):
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
        required = ["base", "start", "end", "tip"]
        missing = [class_name for class_name in required if class_name not in best]
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
        start = self._bbox_center(best["start"])
        end = self._bbox_center(best["end"])
        tip = self._bbox_center(best["tip"])

        start_angle = self._angle_degrees(base, start)
        end_angle = self._angle_degrees(base, end)
        tip_angle = self._angle_degrees(base, tip)
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
            "detected": bool(detections),
            "detector_type": "meter_keypoint_detector",
            "model_backend": self.model_backend,
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error,
        }
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.publisher.publish(msg)
        self.get_logger().info(
            f"Published meter result. station_id={station_id}, "
            f"meter_status={meter_status}, count={len(detections)}, max_conf={max_conf:.4f}, "
            f"reading_status={reading['reading_status']}, reading_value={reading['reading_value']}"
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
