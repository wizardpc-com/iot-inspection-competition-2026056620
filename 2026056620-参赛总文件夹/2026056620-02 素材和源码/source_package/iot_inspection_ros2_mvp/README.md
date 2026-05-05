# 电力场景智能机器人巡检 ROS2 MVP

本项目是面向物联网应用类比赛演示的 ROS2 Humble + Python + YOLO 原型系统。当前版本不依赖真实摄像头，不使用自定义 msg，不使用 `sensor_msgs/Image` 和 `cv_bridge`，通过 `std_msgs/String` 传递 JSON 格式的图片路径和识别结果。

当前系统接入两路视觉分支：

- 管道裂缝检测：`crack_detector_node` 加载裂缝模型并发布 `/vision/crack_result`。
- 仪表检测与估算读数：`meter_detector_node` 加载仪表模型，检测仪表关键部件，并基于 `base/start/end/tip` 的几何关系输出估算读数。默认仍可使用 `meter_stub_node` 作为兼容演示模式。

## 系统闭环

1. `image_source_node` 从 `demo_images/` 循环发布巡检图片路径。
2. `crack_detector_node` 加载 `models/crack_best.pt`，进行管道裂缝检测，并保存带框结果图。
3. `meter_stub_node` 默认发布兼容仪表结果；传入 `use_meter_stub:=false` 后由 `meter_detector_node` 执行仪表关键部件检测与估算读数。
4. `inspection_manager_node` 根据裂缝结果和仪表检测状态发布 `/inspection/state` 与 `/inspection/report`。
5. 裂缝达到阈值时进入 `ALERT` 并发布停车 `/cmd_vel`；仪表检测失败或需复核时进入 `CHECK_METER`。
6. `fake_base_node` 订阅 `/cmd_vel`，打印模拟小车前进、停止或转向。

## 模型和图片放置

裂缝模型：

```text
iot_inspection_ros2_mvp/models/crack_best.pt
```

仪表关键部件检测模型：

```text
iot_inspection_ros2_mvp/models/meter_best.pt
```

可选仪表 last 模型：

```text
iot_inspection_ros2_mvp/models/meter_last.pt
```

演示图片：

```text
iot_inspection_ros2_mvp/demo_images/
```

## 环境安装

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp
python3 -m pip install -r requirements.txt
```

## 构建

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
```

## 运行

默认兼容演示模式，使用 `meter_stub_node`：

```bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

启用真实仪表关键部件检测与估算读数：

```bash
ros2 launch inspection_mvp inspection_demo.launch.py use_meter_stub:=false
```

## 关键配置

配置文件：

```text
ros2_ws/src/inspection_mvp/config/demo.yaml
```

仪表读数相关参数：

```yaml
meter_min_value: 0.0
meter_max_value: 100.0
meter_unit: "unit"
meter_angle_direction: "clockwise"
meter_required_classes: ["base", "start", "end", "tip"]
```

读数方法：以 `base` 为圆心，计算 `start` 到 `end` 的刻度角度范围，再计算 `tip` 的指针角度比例，映射到 `meter_min_value` 到 `meter_max_value` 的量程。

## 查看话题

```bash
ros2 topic list
ros2 topic echo /vision/crack_result
ros2 topic echo /vision/meter_result
ros2 topic echo /inspection/state
ros2 topic echo /inspection/report
ros2 topic echo /cmd_vel
```

## 输出目录

裂缝检测标注图：

```text
outputs/annotated/
```

仪表关键部件检测标注图：

```text
outputs/meter_annotated/
```

## 辅助检查

```bash
python scripts/check_meter_assets.py
python scripts/test_meter_node.py --image demo_images/crack_1.jpg --model models/meter_best.pt
```

## 当前能力边界

当前版本完成 ROS2 仿真闭环、裂缝检测模型接入、仪表关键部件检测与估算读数分支接入、运动反馈接口验证。真实摄像头采集、真实小车底盘、K230 实机部署、激光雷达定位和路径规划属于后续扩展方向。
