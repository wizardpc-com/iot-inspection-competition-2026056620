import json
from datetime import datetime, timezone

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


class InspectionManagerNode(Node):
    """Convert vision results into inspection state, reports, and motion commands."""

    def __init__(self):
        super().__init__("inspection_manager_node")
        self.declare_parameter("normal_speed", 0.1)
        self.declare_parameter("use_meter_stub", True)
        self.normal_speed = (
            self.get_parameter("normal_speed").get_parameter_value().double_value
        )

        self.state_pub = self.create_publisher(String, "/inspection/state", 10)
        self.report_pub = self.create_publisher(String, "/inspection/report", 10)
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.crack_sub = self.create_subscription(
            String, "/vision/crack_result", self._on_crack_result, 10
        )
        self.meter_sub = self.create_subscription(
            String, "/vision/meter_result", self._on_meter_result, 10
        )
        self.latest_meter = None

        self.get_logger().info(
            f"Inspection manager ready. normal_speed={self.normal_speed} m/s"
        )

    def _on_meter_result(self, msg):
        try:
            self.latest_meter = json.loads(msg.data)
            meter_status = self._meter_status(self.latest_meter)
            self.get_logger().info(
                "Meter result received. "
                f"station_id={self.latest_meter.get('station_id')}, "
                f"meter_status={meter_status}, "
                f"reading_status={self.latest_meter.get('reading_status', 'not_available')}"
            )
        except json.JSONDecodeError as exc:
            self.get_logger().error(f"Invalid JSON on /vision/meter_result: {exc}")

    def _on_crack_result(self, msg):
        try:
            result = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().error(f"Invalid JSON on /vision/crack_result: {exc}")
            return

        station_id = result.get("station_id", "UNKNOWN")
        detected = bool(result.get("detected", False))
        max_conf = float(result.get("max_conf", 0.0))
        threshold = float(result.get("threshold", 0.5))

        crack_alert = detected and max_conf >= threshold
        meter_status = self._meter_status(self.latest_meter)
        if crack_alert:
            state = "ALERT"
            reason = f"Pipe crack detected, max_conf={max_conf:.4f} >= threshold={threshold:.4f}"
            suggested_action = "stop_robot_and_request_manual_check"
            cmd = self._make_twist(0.0, 0.0)
        elif meter_status in {"error", "needs_review"}:
            state = "CHECK_METER"
            reason = f"Meter key-part detection status requires review: meter_status={meter_status}"
            suggested_action = "pause_and_review_meter_detection"
            cmd = self._make_twist(0.0, 0.0)
        else:
            state = "NORMAL"
            reason = f"No crack above threshold, max_conf={max_conf:.4f}, threshold={threshold:.4f}"
            suggested_action = "continue_inspection"
            cmd = self._make_twist(self.normal_speed, 0.0)

        state_payload = {
            "state": state,
            "station_id": station_id,
            "reason": reason,
            "suggested_action": suggested_action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._publish_state(state_payload)
        self._publish_report(result, state_payload)
        self.cmd_pub.publish(cmd)

        self.get_logger().info(
            f"Inspection decision published. station_id={station_id}, "
            f"state={state}, suggested_action={suggested_action}"
        )

    @staticmethod
    def _make_twist(linear_x, angular_z):
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        return msg

    def _publish_state(self, payload):
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.state_pub.publish(msg)

    @staticmethod
    def _meter_status(meter_result):
        if not meter_result:
            return "not_available"
        return meter_result.get("meter_status") or meter_result.get("status") or "not_available"

    def _publish_report(self, crack_result, state_payload):
        meter_text = "meter=not_available"
        if self.latest_meter:
            meter_status = self._meter_status(self.latest_meter)
            meter_reason = self.latest_meter.get("reason", "")
            reading_status = self.latest_meter.get("reading_status", "not_available")
            reading_value = self.latest_meter.get("reading_value", None)
            reading_unit = self.latest_meter.get("reading_unit", "")
            meter_text = (
                f"meter_status={meter_status}, "
                f"reading_status={reading_status}, "
                f"reading_value={reading_value}, "
                f"reading_unit={reading_unit}, "
                f"meter_reason={meter_reason}"
            )

        report = (
            f"[Inspection Report] station={state_payload['station_id']} | "
            f"state={state_payload['state']} | "
            f"crack_count={crack_result.get('count', 0)} | "
            f"max_conf={crack_result.get('max_conf', 0.0)} | "
            f"{meter_text} | "
            f"action={state_payload['suggested_action']} | "
            f"annotated_image={crack_result.get('annotated_image_path', '')}"
        )
        msg = String()
        msg.data = report
        self.report_pub.publish(msg)
        self.get_logger().info(report)


def main(args=None):
    rclpy.init(args=args)
    node = InspectionManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Inspection manager interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
