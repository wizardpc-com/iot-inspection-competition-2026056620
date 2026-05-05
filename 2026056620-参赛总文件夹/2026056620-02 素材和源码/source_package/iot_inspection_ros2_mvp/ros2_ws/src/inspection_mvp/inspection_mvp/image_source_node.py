import json
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ImageSourceNode(Node):
    """Publish demo image paths as JSON messages."""

    def __init__(self):
        super().__init__("image_source_node")
        self.declare_parameter("image_dir", "../demo_images")
        self.declare_parameter("publish_interval", 2.0)
        self.declare_parameter("loop_images", True)

        self.image_dir = self._resolve_path(
            self.get_parameter("image_dir").get_parameter_value().string_value
        )
        self.publish_interval = (
            self.get_parameter("publish_interval").get_parameter_value().double_value
        )
        self.loop_images = (
            self.get_parameter("loop_images").get_parameter_value().bool_value
        )

        self.publisher = self.create_publisher(String, "/inspection/image_path", 10)
        self.images = []
        self.index = 0

        self._reload_images()
        self.timer = self.create_timer(self.publish_interval, self._publish_next_image)

        self.get_logger().info(
            f"Image source ready. image_dir={self.image_dir}, "
            f"publish_interval={self.publish_interval}s, loop_images={self.loop_images}"
        )

    @staticmethod
    def _resolve_path(path_text):
        return Path(path_text).expanduser().resolve()

    def _reload_images(self):
        if not self.image_dir.exists():
            self.get_logger().error(
                f"Demo image directory does not exist: {self.image_dir}. "
                "Create it and put jpg/png/jpeg files inside."
            )
            self.images = []
            return

        patterns = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
        images = []
        for pattern in patterns:
            images.extend(self.image_dir.glob(pattern))
        self.images = sorted({path.resolve() for path in images})

        if not self.images:
            self.get_logger().error(
                f"No demo images found in {self.image_dir}. "
                "Supported formats: jpg, jpeg, png. Node will keep waiting."
            )
        else:
            self.get_logger().info(f"Loaded {len(self.images)} demo image(s).")

    def _publish_next_image(self):
        if not self.images:
            self._reload_images()
            return

        if self.index >= len(self.images):
            if not self.loop_images:
                self.get_logger().info("All demo images have been published once.")
                return
            self.index = 0

        image_path = self.images[self.index]
        station_id = f"P{self.index + 1:03d}"
        self.index += 1

        payload = {
            "station_id": station_id,
            "image_path": str(image_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_type": "demo_image",
        }
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.publisher.publish(msg)
        self.get_logger().info(
            f"Published image path. station_id={station_id}, image_path={image_path}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = ImageSourceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Image source interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
