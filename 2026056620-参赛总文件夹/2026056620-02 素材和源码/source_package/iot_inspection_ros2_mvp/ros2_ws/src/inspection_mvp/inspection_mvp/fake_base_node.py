import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class FakeBaseNode(Node):
    """Print simulated base behavior from /cmd_vel."""

    def __init__(self):
        super().__init__("fake_base_node")
        self.subscription = self.create_subscription(
            Twist, "/cmd_vel", self._on_cmd_vel, 10
        )
        self.get_logger().info("Fake base ready. Listening to /cmd_vel.")

    def _on_cmd_vel(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        if abs(linear_x) < 1e-6 and abs(angular_z) < 1e-6:
            action = "模拟小车停止"
        elif abs(angular_z) >= 1e-6:
            action = "模拟小车转向"
        else:
            action = "模拟小车前进"

        self.get_logger().info(
            f"{action}: linear.x={linear_x:.3f}, angular.z={angular_z:.3f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = FakeBaseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Fake base interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
