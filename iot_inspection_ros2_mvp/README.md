# 电力场景智能机器人巡检 ROS2 MVP

本目录是参赛作品的核心运行系统，使用 ROS2 Humble、Python、Ultralytics YOLO 和标准 ROS2 话题构建。系统不依赖真实摄像头，图片由 `demo_images/` 提供；不使用自定义消息，所有视觉输入和识别结果均通过 `std_msgs/String` 承载 JSON 字符串。

## 系统流程

1. `image_source_node` 周期性扫描 `demo_images/`，把图片绝对路径发布到 `/inspection/image_path`。
2. `crack_detector_node` 启动时通过 `ultralytics.YOLO` 加载 `models/crack_best.pt`，收到图片路径后完成裂缝检测，发布 `/vision/crack_result`，并将带框图保存到 `outputs/annotated/`。
3. `meter_detector_node` 通过本地 YOLOv5 `detect.py` 调用 `models/meter_best.pt`，收到图片路径后完成仪表关键部件检测，发布 `/vision/meter_result`，并将带框图保存到 `outputs/meter_annotated/`。
4. `inspection_manager_node` 汇总裂缝和仪表结果，发布 `/inspection/state`、`/inspection/report` 和 `/cmd_vel`。
5. `fake_base_node` 订阅 `/cmd_vel`，用日志模拟小车运动反馈。当前演示假设小车持续前进，因此管理节点会持续发布小速度前进指令。

`inspection_manager_node` 会定时发布当前状态。图片目录为空或尚未收到视觉结果时，状态为 `IDLE`，便于录屏时确认系统已经启动。

## 模型和图片

```text
models/crack_best.pt        裂缝检测模型
models/meter_best.pt        仪表关键部件检测模型，YOLOv5 旧格式权重
models/yolov5/detect.py     YOLOv5 兼容推理入口
demo_images/                演示图片目录，可同时放裂缝图片和仪表图片
```

两个视觉节点都会订阅 `/inspection/image_path`。如果图片中没有对应目标，节点会正常发布 `detected=false` 或 `needs_review`，不会导致系统崩溃。

## 构建和运行

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

## 常用观察命令

```bash
ros2 topic list
ros2 topic echo /inspection/image_path --once
ros2 topic echo /vision/crack_result --once
ros2 topic echo /vision/meter_result --once
ros2 topic echo /inspection/state --once
ros2 topic echo /inspection/report --once
ros2 topic echo /cmd_vel --once
```

## 仪表估算读数说明

当前仪表模型的主要能力是检测仪表关键部件。系统以 `base` 为中心，计算 `start`、`end` 和 `tip` 的相对角度，将指针角度在起止刻度之间的比例映射到配置量程，得到 `reading_value`。该读数适合作为比赛原型演示中的估算结果，后续可针对具体仪表量程、刻度方向和非线性表盘进行标定。

相关参数位于：

```text
ros2_ws/src/inspection_mvp/config/demo.yaml
```

## 输出目录

```text
outputs/annotated/          裂缝检测标注图
outputs/meter_annotated/    仪表关键部件检测标注图
```

## 当前边界

当前版本已经完成 ROS2 仿真流程、裂缝检测模型接入、仪表关键部件检测与估算读数分支接入、状态汇总和模拟运动反馈。真实摄像头采集、真实底盘控制、K230 边缘部署、激光雷达定位和路径规划为后续扩展方向。
