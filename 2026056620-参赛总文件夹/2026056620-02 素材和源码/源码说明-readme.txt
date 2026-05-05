源码说明

当前源码对应 iot_inspection_ros2_mvp，系统不依赖真实摄像头和真实小车，重点验证电力场景下的 ROS2 仿真与 AI视觉识别闭环。

运行步骤：

```bash
cd iot_inspection_ros2_mvp
python3 -m pip install -r requirements.txt

source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

查看话题：

```bash
ros2 topic list
ros2 topic echo /vision/crack_result --once
ros2 topic echo /inspection/state --once
ros2 topic echo /inspection/report --once
```

裂缝模型放置：iot_inspection_ros2_mvp/models/crack_best.pt
仪表模型放置：iot_inspection_ros2_mvp/models/meter_best.pt
图片放置：iot_inspection_ros2_mvp/demo_images/
结果目录：iot_inspection_ros2_mvp/outputs/annotated/
