# Demo Script

本脚本用于 5-8 分钟演示视频录制。演示重点是当前已完成的 ROS2 仿真系统和双视觉模型推理流程。

## 0:00-0:40 项目背景

介绍电力巡检中管道裂缝、仪表状态观察和巡检记录一致性的需求。说明当前作品不是完整真实机器人系统，而是面向比赛展示的 ROS2 仿真原型。

## 0:40-1:20 系统方案

说明当前系统使用本地图片模拟巡检输入，通过 ROS2 话题连接图像输入、裂缝识别、仪表关键部件检测、状态汇总和模拟运动接口。强调两个模型均由 ROS2 节点直接加载。

## 1:20-2:10 节点架构

展示 `image_source_node`、`crack_detector_node`、`meter_detector_node`、`inspection_manager_node` 和 `fake_base_node`。说明后续新增视觉模块可以继续订阅 `/inspection/image_path` 并发布自己的 `/vision/..._result`。

## 2:10-3:00 系统启动

展示命令：

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

说明节点启动后会周期发布状态和小车前进指令。若 `demo_images/` 暂时为空，状态会保持 `IDLE`。

## 3:00-4:10 裂缝识别

展示 `/vision/crack_result`：

```bash
ros2 topic echo /vision/crack_result --once
```

展示 `detected`、`count`、`max_conf`、`detections` 和 `annotated_image_path`，再打开 `outputs/annotated/` 查看裂缝标注图。

## 4:10-5:20 仪表检测与估算读数

展示 `/vision/meter_result`：

```bash
ros2 topic echo /vision/meter_result --once
```

展示 `meter_status`、`class_counts`、`reading_status`、`reading_value`、`reading_ratio` 和 `annotated_image_path`，再打开 `outputs/meter_annotated/` 查看仪表关键部件标注图。

## 5:20-6:20 状态汇总与运动接口

展示：

```bash
ros2 topic echo /inspection/state --once
ros2 topic echo /inspection/report --once
ros2 topic echo /cmd_vel --once
```

说明当前演示策略是假设小车持续前进，`/cmd_vel` 默认输出 `linear.x=0.1`，真实底盘接入后可替换 `fake_base_node`。

## 6:20-7:20 结果图与后续扩展

展示 `outputs/annotated/` 和 `outputs/meter_annotated/`。总结当前已完成双视觉模型接入、ROS2 话题通信、状态汇总和结果保存；后续可接入真实摄像头、真实底盘、K230 边缘推理、激光雷达定位和更多电力设备识别模块。
