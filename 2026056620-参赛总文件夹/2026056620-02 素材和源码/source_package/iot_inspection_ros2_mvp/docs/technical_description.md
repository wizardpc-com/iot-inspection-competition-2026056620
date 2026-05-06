# Technical Description

## 作品概述

本项目面向电力巡检场景，当前版本聚焦 ROS2 仿真系统与 AI 视觉识别原型。系统使用本地图片模拟巡检图像输入，直接调用裂缝检测模型和仪表关键部件检测模型，完成“图片路径发布、双视觉模型推理、ROS2 结果发布、状态汇总、模拟小车前进、结果图保存”的演示流程。

## 为什么使用 ROS2

ROS2 适合把巡检系统拆成多个职责清晰的节点。图像输入、裂缝识别、仪表识别、状态管理和运动接口可以独立运行，通过话题通信完成协作。后续接入真实摄像头、底盘、边缘端设备或新的 AI 模块时，只需要替换或新增节点，已有话题接口可以继续复用。

## 节点架构

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

image_source_node
    ↓ /inspection/image_path
meter_detector_node
    ↓ /vision/meter_result
inspection_manager_node
```

## 裂缝检测节点

`crack_detector_node` 启动时加载 `models/crack_best.pt`，收到 `/inspection/image_path` 后调用 `ultralytics.YOLO` 推理。节点输出检测框、类别、置信度、最大置信度、阈值和结果图路径，并将标注图保存到 `outputs/annotated/`。

## 仪表检测节点

`meter_detector_node` 通过本地 YOLOv5 `detect.py` 调用 `models/meter_best.pt`，检测仪表关键部件。当前配置关注 `base`、`start`、`end`、`tip` 四类：`base` 表示指针或表盘中心参考点，`start` 和 `end` 表示量程起止位置，`tip` 表示指针端点。节点解析 YOLOv5 `labels/*.txt`，发布 `/vision/meter_result`，并将标注图保存到 `outputs/meter_annotated/`。

当四类关键部件齐全时，系统根据几何角度关系估算读数：

```text
以 base 为中心
计算 start、end、tip 的相对角度
计算 tip 在 start 到 end 之间的比例
映射到 demo.yaml 中配置的 meter_min_value 和 meter_max_value
```

该读数是原型系统中的估算结果，后续可以根据具体仪表量程、刻度方向、非线性刻度和现场标定继续优化。

## 巡检管理节点

`inspection_manager_node` 订阅 `/vision/crack_result` 和 `/vision/meter_result`，将两路视觉结果汇总为 `/inspection/state` 和 `/inspection/report`。当前演示不做停车控制，假设小车持续前进，因此节点会持续向 `/cmd_vel` 发布默认小速度。

## 扩展方式

后续新增模块时建议遵循以下方式：

- 新增独立节点，例如 `temperature_detector_node`、`smoke_detector_node` 或真实摄像头节点。
- 需要图像输入的节点订阅 `/inspection/image_path`。
- 识别结果发布到 `/vision/<module>_result`，继续使用 `std_msgs/String` JSON。
- `inspection_manager_node` 只增加结果汇总逻辑，不影响已有裂缝和仪表节点。
- 真实底盘可替换 `fake_base_node`，继续订阅 `/cmd_vel`。

## 当前边界

当前版本不依赖真实摄像头、真实底盘、K230 实机、激光雷达 SLAM、Nav2、自主导航、无人机或机械臂。上述内容属于后续工程扩展方向。
