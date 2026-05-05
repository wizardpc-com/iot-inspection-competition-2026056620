# 电力场景智能机器人巡检 ROS2 MVP

这是一个面向比赛演示的最小可运行 ROS2 Humble + Python + YOLO 项目。系统不依赖真实摄像头，不使用自定义 msg，不使用 `sensor_msgs/Image` 和 `cv_bridge`，而是用 `std_msgs/String` 传递 JSON 格式的图片路径，降低最后一天集成风险。

## 系统闭环

1. `image_source_node` 从 `demo_images/` 循环发布巡检图片路径。
2. `crack_detector_node` 加载 `models/best.pt`，对图片进行管道裂缝检测，并保存带框结果图。
3. `inspection_manager_node` 根据检测结果判断 `NORMAL` 或 `ALERT`。
4. `ALERT` 时发布 `/cmd_vel` 零速度停车指令，`NORMAL` 时发布低速前进指令。
5. `fake_base_node` 打印模拟小车动作，证明运动控制接口已预留。
6. `meter_stub_node` 模拟仪表识别结果，证明第二路 AI 视觉接口已预留。

## 文件结构

```text
iot_inspection_ros2_mvp/
├── README.md
├── requirements.txt
├── docs/
├── demo_images/
├── models/
├── outputs/
└── ros2_ws/
    └── src/
        └── inspection_mvp/
            ├── package.xml
            ├── setup.py
            ├── setup.cfg
            ├── inspection_mvp/
            ├── launch/
            └── config/
```

## 环境安装

先安装 ROS2 Humble，并确认可以使用：

```bash
source /opt/ros/humble/setup.bash
ros2 --version
```

安装 Python 依赖：

```bash
cd iot_inspection_ros2_mvp
python3 -m pip install -r requirements.txt
```

## 放置模型和图片

把训练好的 YOLO 模型放到：

```text
iot_inspection_ros2_mvp/models/best.pt
```

把演示图片放到：

```text
iot_inspection_ros2_mvp/demo_images/
```

支持 `.jpg`、`.jpeg`、`.png`。

## 构建

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
```

## 运行

```bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

默认配置在：

```text
ros2_ws/src/inspection_mvp/config/demo.yaml
```

如果需要调整模型、图片或输出路径，优先修改这个配置文件。默认路径均相对于 `ros2_ws` 运行目录：

```yaml
image_dir: "../demo_images"
model_path: "../models/best.pt"
output_dir: "../outputs/annotated"
conf_threshold: 0.5
publish_interval: 2.0
```

## 查看话题

```bash
ros2 topic list
ros2 topic echo /vision/crack_result
ros2 topic echo /inspection/state
ros2 topic echo /inspection/report
ros2 topic echo /cmd_vel
```

## 展示节点关系

```bash
rqt_graph
```

建议录屏时同时展示：

- 终端启动日志
- `/vision/crack_result`
- `/inspection/state`
- `/inspection/report`
- `outputs/annotated/` 中生成的结果图
- `rqt_graph` 节点关系图

## 常见错误

模型不存在：

```text
YOLO model file not found
```

处理方式：确认 `models/best.pt` 已放好，或者在 `demo.yaml` 修改 `model_path`。

图片目录为空：

```text
No demo images found
```

处理方式：把 `.jpg/.jpeg/.png` 图片放入 `demo_images/`。

找不到 ROS2 包：

```text
Package 'inspection_mvp' not found
```

处理方式：确认已经在 `ros2_ws` 下执行 `colcon build`，并执行 `source install/setup.bash`。

推理窗口阻塞：

本项目没有使用 `show=True`，不会打开阻塞窗口。检测结果保存到 `outputs/annotated/`。

## MVP 边界

本项目只做比赛演示闭环，不包含训练逻辑、不修改 `data.yaml`、不使用真实摄像头、不引入 Nav2、无人机或机械臂逻辑。后续可把图片路径输入替换为真实相机采集模块，也可把 `meter_stub_node` 替换为真实仪表识别模型。
