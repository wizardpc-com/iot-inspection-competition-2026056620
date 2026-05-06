from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    default_config = PathJoinSubstitution(
        [FindPackageShare("inspection_mvp"), "config", "demo.yaml"]
    )
    config_file = LaunchConfiguration("config_file")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=default_config,
                description="Path to demo YAML config file.",
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
                executable="meter_detector_node",
                name="meter_detector_node",
                output="screen",
                parameters=[config_file],
            ),
        ]
    )
