# 电力场景下的智能机器人巡检系统

作品编号：2026056620  
作品类别：物联网应用 - 行业应用  
比赛方向：中国大学生计算机设计大赛物联网应用类相关赛道

本仓库用于保存参赛作品源码、运行说明和提交材料。当前版本是一个 ROS2 仿真系统与 AI 视觉识别原型，围绕电力巡检中的管道裂缝识别和仪表观察构建双视觉模型流程：图片输入、裂缝检测、仪表关键部件检测、仪表估算读数、ROS2 结果发布、巡检状态汇总、模拟小车持续前进和结果图保存。

## 当前已完成内容

- 使用 ROS2 Humble 和 Python 构建 `inspection_mvp` 包。
- 使用 `std_msgs/String` 传递 JSON，不使用自定义 msg、`sensor_msgs/Image` 或 `cv_bridge`。
- `image_source_node` 从 `demo_images/` 发布图片路径到 `/inspection/image_path`。
- `crack_detector_node` 加载 `models/crack_best.pt`，发布 `/vision/crack_result`，保存裂缝标注图。
- `meter_detector_node` 通过本地 YOLOv5 `detect.py` 调用 `models/meter_best.pt`，发布 `/vision/meter_result`，保存仪表关键部件标注图，并在检测到 `base/start/end/tip` 时输出估算读数。
- `inspection_manager_node` 汇总裂缝和仪表结果，发布 `/inspection/state`、`/inspection/report` 和 `/cmd_vel`。
- 当前演示策略是假设小车持续前进，`/cmd_vel` 持续发布小速度前进指令。

## 仓库结构

```text
iot_inspection_ros2_mvp/        ROS2 Python 原型系统源码
model_reference/                模型训练配置与原始推理脚本参考
scripts/                        参赛材料生成、源码打包和结构检查脚本
2026056620-参赛总文件夹/        面向评委和队友共享的提交材料目录
```

## 运行方式

```bash
cd iot_inspection_ros2_mvp
python3 -m pip install -r requirements.txt
cd models
git clone https://github.com/ultralytics/yolov5.git yolov5
cd yolov5
python3 -m pip install -r requirements.txt
cd ../..

source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

## 关键话题

```bash
ros2 topic list
ros2 topic echo /inspection/image_path --once
ros2 topic echo /vision/crack_result --once
ros2 topic echo /vision/meter_result --once
ros2 topic echo /inspection/state --once
ros2 topic echo /inspection/report --once
ros2 topic echo /cmd_vel --once
```

## 能力边界

当前作品展示的是 ROS2 仿真系统和 AI 视觉识别原型。真实小车底盘、真实摄像头、K230 实机部署、激光雷达定位、路径规划、无人机和机械臂不属于当前已完成内容，可作为后续工程扩展方向。
