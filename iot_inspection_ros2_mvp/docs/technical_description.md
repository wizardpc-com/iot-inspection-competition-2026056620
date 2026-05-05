# Technical Description

## 为什么使用 ROS2

ROS2 适合机器人系统的模块化开发。巡检机器人通常包含感知、决策、运动控制、日志记录和可视化等多个模块。使用 ROS2 可以把这些模块拆成独立节点，通过话题进行通信，便于演示、调试和后续替换。

本项目使用 ROS2 Humble 和 Python，是因为 Humble 稳定性好，Python 生态中可以直接调用 Ultralytics YOLO，适合比赛 MVP 快速集成。

## 为什么使用模块化节点

本项目把系统拆成五个节点：

- `image_source_node`：负责巡检图片输入
- `crack_detector_node`：负责裂缝检测
- `inspection_manager_node`：负责状态判断和控制指令
- `fake_base_node`：负责模拟底盘响应
- `meter_stub_node`：负责模拟第二路仪表识别接口

这种拆分可以让每个模块职责清晰。后续替换真实相机、真实底盘或新的 AI 模型时，只需要替换对应节点，不影响其他部分。

## 裂缝检测节点原理

`crack_detector_node` 启动时读取 `model_path` 参数，并使用 `ultralytics.YOLO` 加载 `best.pt`。模型只加载一次，避免每张图片重复初始化带来的延迟和不稳定。

节点订阅 `/inspection/image_path`，从 JSON 中解析图片路径。收到图片后调用：

```python
model.predict(source=image_path, conf=conf_threshold, save=False, show=False)
```

推理完成后，节点解析 YOLO 输出框，生成包含 `bbox`、`conf`、`class_id` 和 `class_name` 的 JSON，并保存带检测框的图片到 `outputs/annotated/`。

如果图片不存在、模型不存在或推理失败，节点不会崩溃，而是发布 `detected=false` 的错误结果，保证演示系统继续运行。

## 任务管理节点原理

`inspection_manager_node` 订阅 `/vision/crack_result` 和 `/vision/meter_result`。当前决策规则聚焦裂缝检测：

```text
detected == true 且 max_conf >= threshold -> ALERT
否则 -> NORMAL
```

当状态为 `ALERT` 时，节点发布零速度 `/cmd_vel`，表示停车并请求人工复核。当状态为 `NORMAL` 时，节点发布低速前进指令，表示继续巡检。

同时，节点发布两类上层信息：

- `/inspection/state`：机器可读 JSON 状态
- `/inspection/report`：便于比赛展示的人类可读报告

## 当前 MVP 与后续接入关系

当前 MVP 使用 `std_msgs/String` 传 JSON 图片路径，而不是直接传图像消息。这是为了降低比赛最后一天的环境风险，避免 `cv_bridge`、图像编码和真实摄像头驱动带来的额外问题。

后续接入真实小车时，可以逐步替换：

- 真实相机或 K230 图像采集节点替换 `image_source_node`
- 真实仪表识别模型替换 `meter_stub_node`
- 真实底盘控制节点替换 `fake_base_node`
- 保留 `/vision/crack_result`、`/inspection/state`、`/cmd_vel` 等接口

这种设计让 MVP 演示和后续工程化之间保持一致的接口边界。
