from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    default_config = PathJoinSubstitution(
        [FindPackageShare("inspection_mvp"), "config", "demo.yaml"]
    )
    config_file = LaunchConfiguration("config_file")
    use_meter_stub = LaunchConfiguration("use_meter_stub")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=default_config,
                description="Path to demo YAML config file.",
            ),
            DeclareLaunchArgument(
                "use_meter_stub",
                default_value="true",
                description="Use meter_stub_node when true; use meter_detector_node when false.",
            ),
            Node(
                package="inspection_mvp",
                executable="image_source_node",
                name="image_source_node",
                output="screen",
                parameters=[config_file],
            ),
            Node(
                package="inspection_mvp",
                executable="crack_detector_node",
                name="crack_detector_node",
                output="screen",
                parameters=[config_file],
            ),
            Node(
                package="inspection_mvp",
                executable="inspection_manager_node",
                name="inspection_manager_node",
                output="screen",
                parameters=[config_file],
            ),
            Node(
                package="inspection_mvp",
                executable="fake_base_node",
                name="fake_base_node",
                output="screen",
            ),
            Node(
                package="inspection_mvp",
                executable="meter_stub_node",
                name="meter_stub_node",
                output="screen",
                parameters=[config_file, {"use_meter_stub": use_meter_stub}],
                condition=IfCondition(use_meter_stub),
            ),
            Node(
                package="inspection_mvp",
                executable="meter_detector_node",
                name="meter_detector_node",
                output="screen",
                parameters=[config_file, {"use_meter_stub": use_meter_stub}],
                condition=UnlessCondition(use_meter_stub),
            ),
        ]
    )
