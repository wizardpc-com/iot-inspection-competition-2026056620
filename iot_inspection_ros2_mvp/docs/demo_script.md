# Demo Script

本脚本适合组织 5 到 8 分钟比赛演示视频。

## 1. 项目背景

介绍电力场景中的巡检需求：管道、设备外观、仪表状态都需要稳定巡检。传统人工巡检效率低、记录不统一，机器人巡检可以把图像采集、AI 识别、状态判断和运动控制串成闭环。

## 2. 系统架构

展示 ROS2 节点图或架构图，说明系统由五个节点组成：

- 图片输入节点
- 裂缝检测节点
- 巡检管理节点
- 模拟底盘节点
- 仪表识别占位节点

强调本 MVP 不依赖真实摄像头，使用图片路径消息完成稳定演示。

## 3. ROS2 节点启动

打开终端，执行：

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

讲解启动日志：YOLO 模型加载、图片目录读取、管理节点和模拟底盘启动。

## 4. 图片巡检输入

展示 `demo_images/` 目录中的图片。说明 `image_source_node` 每 2 秒发布一张图片路径到 `/inspection/image_path`，JSON 中包含站点编号、绝对图片路径、时间戳和输入类型。

可执行：

```bash
ros2 topic echo /inspection/image_path
```

## 5. 裂缝识别

展示 `/vision/crack_result`：

```bash
ros2 topic echo /vision/crack_result
```

说明 `crack_detector_node` 收到图片路径后调用 YOLO 模型推理，输出检测框、置信度、数量、最大置信度和结果图路径。推理结果图保存到 `outputs/annotated/`。

## 6. ALERT 状态反馈

展示 `/inspection/state`：

```bash
ros2 topic echo /inspection/state
```

说明当 `detected=true` 且 `max_conf >= conf_threshold` 时，巡检状态变为 `ALERT`；否则为 `NORMAL`。即使没有检测到裂缝，也会输出稳定的 NORMAL 结果。

## 7. 小车停止指令

展示 `/cmd_vel` 和 `fake_base_node` 日志：

```bash
ros2 topic echo /cmd_vel
```

讲解 `ALERT` 时系统发布 `linear.x=0.0`、`angular.z=0.0`，模拟停车；`NORMAL` 时发布 `linear.x=0.1`，模拟继续巡检。

## 8. 结果图和日志展示

打开 `outputs/annotated/`，展示带检测框的结果图。终端中同时展示：

- YOLO 推理日志
- 巡检报告日志
- 模拟小车前进或停止日志

可执行：

```bash
ros2 topic echo /inspection/report
```

## 9. 后续扩展

说明当前系统是最后一天稳定优先的 MVP，后续可以扩展：

- 将图片路径输入替换为真实相机采集节点
- 将 `meter_stub_node` 替换为真实仪表识别模型
- 接入真实底盘控制器
- 接入 K230 或边缘计算设备
- 接入数据库和 Web 可视化平台
