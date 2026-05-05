# Demo Script

本脚本用于组织 5-8 分钟作品演示视频。

## 0:00-0:40 项目背景

介绍电力巡检中管道裂缝、设备外观和仪表状态识别需求。说明当前系统聚焦 ROS2 仿真闭环和 AI 视觉检测接入。

## 0:40-1:20 系统方案

展示系统架构：图片输入、裂缝检测、仪表关键部件检测与估算读数、巡检状态管理、模拟运动反馈。

## 1:20-2:10 ROS2 节点架构

展示节点和话题：

- `image_source_node`
- `crack_detector_node`
- `meter_stub_node` 或 `meter_detector_node`
- `inspection_manager_node`
- `fake_base_node`

## 2:10-3:20 系统启动

默认兼容演示模式：

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

启用真实仪表关键部件检测与估算读数：

```bash
ros2 launch inspection_mvp inspection_demo.launch.py use_meter_stub:=false
```

## 3:20-4:20 裂缝识别结果

展示 `/vision/crack_result`：

```bash
ros2 topic echo /vision/crack_result
```

展示 `outputs/annotated/` 中带裂缝框的结果图。

## 4:20-5:20 仪表检测与读数

展示 `/vision/meter_result`：

```bash
ros2 topic echo /vision/meter_result
```

说明当前仪表分支检测仪表盘区域、指针、刻度等关键部件，保存结果到 `outputs/meter_annotated/`，并根据 `base/start/end/tip` 的角度关系输出估算读数。

## 5:20-6:20 巡检状态与运动反馈

展示：

```bash
ros2 topic echo /inspection/state
ros2 topic echo /inspection/report
ros2 topic echo /cmd_vel
```

说明裂缝达到阈值时进入 `ALERT`，仪表检测或读数需要复核时进入 `CHECK_METER`，`fake_base_node` 会打印模拟小车停止或前进。

## 6:20-7:20 结果图与扩展

展示：

- `outputs/annotated/`
- `outputs/meter_annotated/`
- 终端日志
- 节点图或 `rqt_graph`

总结当前完成裂缝检测闭环和仪表关键部件检测与估算读数接入。后续可针对不同仪表类型配置量程、方向和刻度标定。
