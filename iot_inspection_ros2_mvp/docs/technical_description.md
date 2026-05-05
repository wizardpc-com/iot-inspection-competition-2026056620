# Technical Description

## 1. 作品概述

本项目面向电力巡检场景，使用 ROS2 Humble、Python 和 YOLO 模型构建智能巡检原型。当前版本完成图像输入、裂缝检测、仪表关键部件检测与估算读数、巡检状态判断、模拟运动反馈和结果图保存。

系统不依赖真实摄像头，不使用自定义 msg，不使用 `sensor_msgs/Image` 和 `cv_bridge`。视觉输入和识别结果通过 `std_msgs/String` 承载 JSON 数据。

## 2. ROS2 节点架构

```text
image_source_node
    ↓ /inspection/image_path
crack_detector_node
    ↓ /vision/crack_result
inspection_manager_node
    ↓ /inspection/state
    ↓ /inspection/report
    ↓ /cmd_vel
fake_base_node

meter_stub_node 或 meter_detector_node
    ↓ /vision/meter_result
inspection_manager_node
```

节点职责：

- `image_source_node`：从 `demo_images/` 发布图片路径。
- `crack_detector_node`：加载 `models/crack_best.pt`，完成管道裂缝检测。
- `meter_stub_node`：默认兼容演示模式，发布稳定的仪表分支结果。
- `meter_detector_node`：加载 `models/meter_best.pt`，完成仪表关键部件检测与估算读数。
- `inspection_manager_node`：融合裂缝与仪表分支结果，发布状态、报告和运动指令。
- `fake_base_node`：订阅 `/cmd_vel` 并打印模拟小车动作。

## 3. 裂缝检测节点

`crack_detector_node` 在启动时加载裂缝模型，只加载一次。节点订阅 `/inspection/image_path`，收到图片路径后调用 Ultralytics YOLO 推理，解析检测框、置信度和类别，并把带框结果图保存到 `outputs/annotated/`。

裂缝检测结果发布到 `/vision/crack_result`。当 `detected=true` 且 `max_conf >= threshold` 时，巡检管理节点进入 `ALERT` 状态。

## 4. 仪表检测与估算读数节点

`meter_detector_node` 是第二路视觉检测分支。该节点订阅 `/inspection/image_path`，对同一张巡检图片执行仪表关键部件检测，并发布 `/vision/meter_result`。

模型信息：

- 模型文件：`models/meter_best.pt`
- 模型来源：YOLOv5s 训练 100 轮，样例 mAP 0.869
- 当前能力：检测仪表盘区域、指针、刻度等关键部件
- 当前输出：检测框、类别、置信度、标注图、估算读数

节点优先使用 `ultralytics.YOLO` 加载模型。若模型不存在或无法加载，节点会发布带 `error` 字段的 `/vision/meter_result`，并保持进程运行，避免影响裂缝检测闭环。

## 5. 仪表读数方法

仪表读数基于 `base/start/end/tip` 四类关键部件的检测框中心点：

1. 以 `base` 的检测框中心作为表盘角度中心。
2. 计算 `start` 和 `end` 相对 `base` 的角度，得到刻度范围。
3. 计算 `tip` 相对 `base` 的角度，得到指针位置。
4. 按 `meter_angle_direction` 计算指针在起止刻度之间的比例 `reading_ratio`。
5. 将比例映射到 `meter_min_value` 到 `meter_max_value`，得到 `reading_value`。

输出字段包括：

- `reading_status`
- `reading_value`
- `reading_unit`
- `reading_ratio`
- `reading_method`
- `reading_reason`

当关键部件缺失时，`reading_status=needs_key_parts`，巡检状态可进入 `CHECK_METER`。

## 6. 仪表状态规则

`meter_detector_node` 根据检测结果给出 `meter_status`：

- `structure_detected`：在 `base/start/end/tip` 等关键类中检测到多数结构。
- `needs_review`：检测结果较少或置信度不足。
- `error`：图片、模型或推理过程出现错误。

## 7. 巡检状态管理

`inspection_manager_node` 保持裂缝优先规则：

```text
裂缝 detected=true 且 max_conf >= threshold -> ALERT
否则 meter_status == error 或 needs_review -> CHECK_METER
否则 -> NORMAL
```

说明：

- `ALERT` 表示裂缝检测达到阈值，发布停车指令并建议复核。
- `CHECK_METER` 表示仪表关键部件检测或读数估计需要复核。
- `NORMAL` 表示当前裂缝与仪表分支无异常状态。

## 8. Launch 模式

默认模式使用 `meter_stub_node`，保持原有演示闭环稳定：

```bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

启用真实仪表关键部件检测与估算读数：

```bash
ros2 launch inspection_mvp inspection_demo.launch.py use_meter_stub:=false
```

## 9. 后续扩展

后续可在当前接口基础上继续扩展：

- 接入真实摄像头图像采集。
- 接入真实小车底盘控制。
- 根据具体仪表类型优化量程、方向和非线性刻度标定。
- 在 K230 或其他边缘设备上部署视觉模型。
- 引入激光雷达定位和路径规划。
