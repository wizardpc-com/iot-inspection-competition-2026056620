from glob import glob
from setuptools import find_packages, setup

package_name = "inspection_mvp"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="inspection_mvp",
    maintainer_email="demo@example.com",
    description="ROS2 Python MVP for power inspection robot crack detection demo.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "image_source_node = inspection_mvp.image_source_node:main",
            "crack_detector_node = inspection_mvp.crack_detector_node:main",
            "inspection_manager_node = inspection_mvp.inspection_manager_node:main",
            "fake_base_node = inspection_mvp.fake_base_node:main",
            "meter_stub_node = inspection_mvp.meter_stub_node:main",
            "meter_detector_node = inspection_mvp.meter_detector_node:main",
        ],
    },
)
