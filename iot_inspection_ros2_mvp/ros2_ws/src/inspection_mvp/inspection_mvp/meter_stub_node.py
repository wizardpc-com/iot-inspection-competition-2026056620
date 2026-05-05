import json
from datetime import datetime, timezone

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MeterStubNode(Node):
    """Publish placeholder meter recognition results."""

    def __init__(self):
        super().__init__("meter_stub_node")
        self.declare_parameter("publish_interval", 5.0)
        self.declare_parameter("station_id", "P001")
        self.declare_parameter("meter_value", 220.0)
        self.declare_parameter("status", "normal")

        self.publish_interval = (
            self.get_parameter("publish_interval").get_parameter_value().double_value
        )
        self.station_id = self.get_parameter("station_id").get_parameter_value().string_value
        self.meter_value = (
            self.get_parameter("meter_value").get_parameter_value().double_value
        )
        self.status = self.get_parameter("status").get_parameter_value().string_value

        self.publisher = self.create_publisher(String, "/vision/meter_result", 10)
        self.timer = self.create_timer(self.publish_interval, self._publish_meter_stub)

        self.get_logger().info(
            "Meter stub ready. This is a placeholder for future meter recognition AI."
        )

    def _publish_meter_stub(self):
        payload = {
            "station_id": self.station_id,
            "detected": True,
            "detector_type": "meter_stub",
            "meter_value": self.meter_value,
            "status": self.status,
            "meter_status": "structure_detected",
            "reading_status": "stub_estimated",
            "reading_value": self.meter_value,
            "reading_unit": "unit",
            "reading_ratio": None,
            "reading_method": "stub_configured_value",
            "reading_reason": "fallback_demo_value",
            "reason": "stub_result_for_compatible_demo_mode",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.publisher.publish(msg)
        self.get_logger().info(
            f"Published meter stub. station_id={self.station_id}, "
            f"meter_value={self.meter_value}, status={self.status}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = MeterStubNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Meter stub interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
