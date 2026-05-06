import json
from datetime import datetime, timezone

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


class InspectionManagerNode(Node):
    """Summarize vision results and keep the simulated robot moving forward."""

    def __init__(self):
        super().__init__("inspection_manager_node")
        self.declare_parameter("normal_speed", 0.1)
        self.declare_parameter("state_publish_interval", 2.0)

        self.normal_speed = (
            self.get_parameter("normal_speed").get_parameter_value().double_value
        )
        self.state_publish_interval = (
            self.get_parameter("state_publish_interval").get_parameter_value().double_value
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

        self.latest_crack = None
        self.latest_meter = None
        self.latest_state = self._make_state(
            state="IDLE",
            station_id="UNKNOWN",
            reason="waiting_for_image_and_vision_results",
            suggested_action="continue_forward_demo",
        )
        self.latest_report = self._build_report()
        self.timer = self.create_timer(
            self.state_publish_interval, self._publish_status_heartbeat
        )

        self.get_logger().info(
            "Inspection manager ready. "
            f"normal_speed={self.normal_speed} m/s, "
            "current demo policy=always_continue_forward"
        )

    def _on_crack_result(self, msg):
        try:
            self.latest_crack = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().error(f"Invalid JSON on /vision/crack_result: {exc}")
            return
        self._update_and_publish("crack_result_received")

    def _on_meter_result(self, msg):
        try:
            self.latest_meter = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().error(f"Invalid JSON on /vision/meter_result: {exc}")
            return
        self._update_and_publish("meter_result_received")

    def _update_and_publish(self, reason):
        station_id = self._latest_station_id()
        state = "NORMAL" if self.latest_crack or self.latest_meter else "IDLE"
        self.latest_state = self._make_state(
            state=state,
            station_id=station_id,
            reason=reason,
            suggested_action="continue_forward_demo",
        )
        self.latest_report = self._build_report()
        self._publish_state(self.latest_state)
        self._publish_report(self.latest_report)
        self._publish_forward_cmd()
        self.get_logger().info(
            f"Inspection summary published. station_id={station_id}, state={state}, "
            "motion=forward"
        )

    def _latest_station_id(self):
        if self.latest_crack:
            return self.latest_crack.get("station_id", "UNKNOWN")
        if self.latest_meter:
            return self.latest_meter.get("station_id", "UNKNOWN")
        return "UNKNOWN"

    @staticmethod
    def _make_state(state, station_id, reason, suggested_action):
        return {
            "state": state,
            "station_id": station_id,
            "reason": reason,
            "suggested_action": suggested_action,
            "motion_policy": "always_forward_in_current_demo",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _crack_summary(self):
        if not self.latest_crack:
            return "crack=not_available"
        return (
            f"crack_detected={self.latest_crack.get('detected', False)}, "
            f"crack_count={self.latest_crack.get('count', 0)}, "
            f"crack_max_conf={self.latest_crack.get('max_conf', 0.0)}, "
            f"crack_image={self.latest_crack.get('annotated_image_path', '')}"
        )

    def _meter_summary(self):
        if not self.latest_meter:
            return "meter=not_available"
        return (
            f"meter_status={self.latest_meter.get('meter_status', 'not_available')}, "
            f"meter_count={self.latest_meter.get('count', 0)}, "
            f"meter_max_conf={self.latest_meter.get('max_conf', 0.0)}, "
            f"reading_status={self.latest_meter.get('reading_status', 'not_available')}, "
            f"reading_value={self.latest_meter.get('reading_value', None)}, "
            f"reading_unit={self.latest_meter.get('reading_unit', '')}, "
            f"meter_image={self.latest_meter.get('annotated_image_path', '')}"
        )

    def _build_report(self):
        return (
            f"[Inspection Report] station={self.latest_state['station_id']} | "
            f"state={self.latest_state['state']} | "
            f"{self._crack_summary()} | "
            f"{self._meter_summary()} | "
            "action=continue_forward_demo"
        )

    def _publish_state(self, payload):
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.state_pub.publish(msg)

    def _publish_report(self, report):
        msg = String()
        msg.data = report
        self.report_pub.publish(msg)
        self.get_logger().info(report)

    def _publish_forward_cmd(self):
        cmd = Twist()
        cmd.linear.x = float(self.normal_speed)
        cmd.angular.z = 0.0
        self.cmd_pub.publish(cmd)

    def _publish_status_heartbeat(self):
        self.latest_state["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._publish_state(self.latest_state)
        self._publish_report(self.latest_report)
        self._publish_forward_cmd()


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
