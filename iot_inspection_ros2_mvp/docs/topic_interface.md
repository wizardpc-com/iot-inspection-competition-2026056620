# Topic Interface

本项目不使用自定义 msg，所有视觉与状态信息均通过 `std_msgs/String` 传 JSON。运动控制接口使用标准 `geometry_msgs/Twist`。

## /inspection/image_path

- 类型：`std_msgs/String`
- 发布者：`image_source_node`
- 订阅者：`crack_detector_node`
- 作用：发布待检测图片路径

示例：

```json
{
  "station_id": "P001",
  "image_path": "/abs/path/to/demo_images/picture_1.jpg",
  "timestamp": "2026-05-05T10:00:00.000000+00:00",
  "source_type": "demo_image"
}
```

## /vision/crack_result

- 类型：`std_msgs/String`
- 发布者：`crack_detector_node`
- 订阅者：`inspection_manager_node`
- 作用：发布管道裂缝检测结果

示例：

```json
{
  "station_id": "P001",
  "image_path": "/abs/path/to/demo_images/picture_1.jpg",
  "annotated_image_path": "/abs/path/to/outputs/annotated/picture_1_annotated.jpg",
  "detected": true,
  "class_name": "pipe_crack",
  "count": 1,
  "max_conf": 0.8732,
  "detections": [
    {
      "bbox": [120.5, 88.0, 260.0, 180.5],
      "conf": 0.8732,
      "class_id": 0,
      "class_name": "pipe_crack"
    }
  ],
  "threshold": 0.5,
  "timestamp": "2026-05-05T10:00:02.000000+00:00"
}
```

无裂缝时：

```json
{
  "station_id": "P002",
  "detected": false,
  "count": 0,
  "max_conf": 0.0,
  "detections": [],
  "threshold": 0.5
}
```

## /vision/meter_result

- 类型：`std_msgs/String`
- 发布者：`meter_stub_node`
- 订阅者：`inspection_manager_node`
- 作用：模拟仪表识别结果，占位接口，后续可替换为真实模型

示例：

```json
{
  "station_id": "P001",
  "detected": true,
  "meter_value": 220.0,
  "status": "normal",
  "timestamp": "2026-05-05T10:00:05.000000+00:00"
}
```

## /inspection/state

- 类型：`std_msgs/String`
- 发布者：`inspection_manager_node`
- 订阅者：演示终端、上层系统
- 作用：发布巡检状态

示例：

```json
{
  "state": "ALERT",
  "station_id": "P001",
  "reason": "Pipe crack detected, max_conf=0.8732 >= threshold=0.5000",
  "suggested_action": "stop_robot_and_request_manual_check",
  "timestamp": "2026-05-05T10:00:03.000000+00:00"
}
```

状态含义：

- `IDLE`：预留状态，表示尚未开始巡检
- `INSPECTING`：预留状态，表示正在巡检
- `NORMAL`：未发现超过阈值的裂缝
- `ALERT`：发现超过阈值的裂缝，需要停车并人工复核

## /inspection/report

- 类型：`std_msgs/String`
- 发布者：`inspection_manager_node`
- 订阅者：演示终端、报告系统
- 作用：发布可读巡检报告

示例：

```text
[Inspection Report] station=P001 | state=ALERT | crack_count=1 | max_conf=0.8732 | meter_status=normal, meter_value=220.0 | action=stop_robot_and_request_manual_check | annotated_image=/abs/path/to/result.jpg
```

## /cmd_vel

- 类型：`geometry_msgs/Twist`
- 发布者：`inspection_manager_node`
- 订阅者：`fake_base_node`
- 作用：预留运动控制接口

规则：

- `ALERT`：`linear.x=0.0`，`angular.z=0.0`，模拟停车
- `NORMAL`：`linear.x=0.1`，`angular.z=0.0`，模拟低速前进
