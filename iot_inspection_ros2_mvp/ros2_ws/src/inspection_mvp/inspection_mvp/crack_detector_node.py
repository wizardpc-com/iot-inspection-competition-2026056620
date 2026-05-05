import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CrackDetectorNode(Node):
    """Run YOLO crack detection for image paths received from ROS2."""

    def __init__(self):
        super().__init__("crack_detector_node")
        self.declare_parameter("model_path", "../models/best.pt")
        self.declare_parameter("conf_threshold", 0.5)
        self.declare_parameter("output_dir", "../outputs/annotated")

        self.model_path = self._resolve_path(
            self.get_parameter("model_path").get_parameter_value().string_value
        )
        self.conf_threshold = (
            self.get_parameter("conf_threshold").get_parameter_value().double_value
        )
        self.output_dir = self._resolve_path(
            self.get_parameter("output_dir").get_parameter_value().string_value
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self._load_model_once()

        self.publisher = self.create_publisher(String, "/vision/crack_result", 10)
        self.subscription = self.create_subscription(
            String, "/inspection/image_path", self._on_image_path, 10
        )

        self.get_logger().info(
            f"Crack detector ready. model_path={self.model_path}, "
            f"conf_threshold={self.conf_threshold}, output_dir={self.output_dir}"
        )

    @staticmethod
    def _resolve_path(path_text):
        return Path(path_text).expanduser().resolve()

    def _load_model_once(self):
        if not self.model_path.exists():
            self.get_logger().error(
                f"YOLO model file not found: {self.model_path}. "
                "Put best.pt under models/best.pt or override model_path."
            )
            return

        try:
            from ultralytics import YOLO

            self.model = YOLO(str(self.model_path))
            self.get_logger().info("YOLO model loaded successfully.")
        except Exception as exc:
            self.get_logger().error(f"Failed to load YOLO model: {exc}")
            self.model = None

    def _on_image_path(self, msg):
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().error(f"Invalid JSON on /inspection/image_path: {exc}")
            return

        station_id = payload.get("station_id", "UNKNOWN")
        image_path = self._resolve_path(payload.get("image_path", ""))
        self.get_logger().info(
            f"Received inspection image. station_id={station_id}, image_path={image_path}"
        )

        if not image_path.exists():
            self.get_logger().error(f"Image file not found: {image_path}")
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                detections=[],
                error="image_not_found",
            )
            return

        if self.model is None:
            self.get_logger().error("YOLO model is unavailable; publishing NORMAL error result.")
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                detections=[],
                error="model_unavailable",
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

            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path=annotated_image_path,
                detections=detections,
            )
        except Exception as exc:
            self.get_logger().error(f"YOLO inference failed: {exc}")
            self._publish_result(
                station_id=station_id,
                image_path=image_path,
                annotated_image_path="",
                detections=[],
                error="inference_failed",
            )

    def _class_name(self, class_id):
        names = getattr(self.model, "names", {}) if self.model is not None else {}
        if isinstance(names, dict):
            return str(names.get(class_id, "pipe_crack"))
        if isinstance(names, list) and 0 <= class_id < len(names):
            return str(names[class_id])
        return "pipe_crack"

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
        output_path = self.output_dir / f"{image_path.stem}_{timestamp}_annotated.jpg"
        cv2.imwrite(str(output_path), annotated)
        self.get_logger().info(f"Annotated result saved: {output_path}")
        return str(output_path.resolve())

    def _publish_result(
        self,
        station_id,
        image_path,
        annotated_image_path,
        detections,
        error=None,
    ):
        max_conf = max((item["conf"] for item in detections), default=0.0)
        detected = bool(detections) and max_conf >= self.conf_threshold
        payload = {
            "station_id": station_id,
            "image_path": str(image_path),
            "annotated_image_path": annotated_image_path,
            "detected": detected,
            "class_name": "pipe_crack",
            "count": len(detections),
            "max_conf": round(max_conf, 4),
            "detections": detections,
            "threshold": self.conf_threshold,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if error:
            payload["error"] = error

        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.publisher.publish(msg)

        status = "ALERT" if detected else "NORMAL"
        self.get_logger().info(
            f"Published crack result. station_id={station_id}, status={status}, "
            f"count={len(detections)}, max_conf={max_conf:.4f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = CrackDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Crack detector interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
