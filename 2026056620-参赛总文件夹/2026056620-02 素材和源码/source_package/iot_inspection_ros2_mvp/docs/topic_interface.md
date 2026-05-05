# Topic Interface

本项目不使用自定义 msg。视觉结果和巡检状态通过 `std_msgs/String` 传 JSON，运动控制接口使用 `geometry_msgs/Twist`。

## /inspection/image_path

- 类型：`std_msgs/String`
- 发布者：`image_source_node`
- 订阅者：`crack_detector_node`、`meter_detector_node`
- 作用：传递巡检图片路径，模拟机器人采集图像

## /vision/crack_result

- 类型：`std_msgs/String`
- 发布者：`crack_detector_node`
- 订阅者：`inspection_manager_node`
- 作用：发布管道裂缝检测结果

## /vision/meter_result

- 类型：`std_msgs/String`
- 发布者：`meter_stub_node` 或 `meter_detector_node`
- 订阅者：`inspection_manager_node`
- 作用：发布仪表关键部件检测与估算读数结果

示例：

```json
{
  "station_id": "P001",
  "image_path": "/abs/path/to/demo_images/meter_1.jpg",
  "annotated_image_path": "/abs/path/to/outputs/meter_annotated/meter_1_meter.jpg",
  "detected": true,
  "detector_type": "meter_keypoint_detector",
  "model_backend": "ultralytics",
  "count": 4,
  "class_counts": {
    "base": 1,
    "start": 1,
    "end": 1,
    "tip": 1
  },
  "max_conf": 0.82,
  "detections": [
    {
      "bbox": [100.0, 90.0, 230.0, 220.0],
      "conf": 0.82,
      "class_id": 0,
      "class_name": "base"
    }
  ],
  "meter_status": "structure_detected",
  "reading_status": "estimated",
  "reading_value": 63.25,
  "reading_unit": "unit",
  "reading_ratio": 0.6325,
  "reading_method": "keypart_angle_linear_scale",
  "reading_reason": "start_angle=220.00,end_angle=20.00,tip_angle=85.00,direction=clockwise",
  "reason": "detected_required_meter_parts=4/4",
  "timestamp": "2026-05-05T10:00:03.000000+00:00",
  "error": null
}
```

字段说明：

- `meter_status=structure_detected`：检测到多数关键部件。
- `meter_status=needs_review`：检测结果较少或置信度不足。
- `meter_status=error`：模型、图片或推理过程出现错误。
- `reading_status=estimated`：已根据关键部件几何关系输出估算读数。
- `reading_status=needs_key_parts`：缺少读数所需关键部件。

## /inspection/state

- 类型：`std_msgs/String`
- 发布者：`inspection_manager_node`
- 作用：发布当前巡检状态

状态含义：

- `NORMAL`：未发现超过阈值的裂缝，仪表分支无错误或复核提示。
- `ALERT`：裂缝检测达到阈值，发布停车指令。
- `CHECK_METER`：仪表关键部件检测或估算读数需要复核。

## /inspection/report

- 类型：`std_msgs/String`
- 发布者：`inspection_manager_node`
- 作用：发布可读巡检报告

示例：

```text
[Inspection Report] station=P001 | state=NORMAL | crack_count=0 | max_conf=0.0 | meter_status=structure_detected, reading_status=estimated, reading_value=63.25, reading_unit=unit, meter_reason=detected_required_meter_parts=4/4 | action=continue_inspection | annotated_image=/abs/path/to/result.jpg
```

## /cmd_vel

- 类型：`geometry_msgs/Twist`
- 发布者：`inspection_manager_node`
- 订阅者：`fake_base_node`
- 作用：预留运动控制接口

规则：

- `ALERT`：`linear.x=0.0`，`angular.z=0.0`，模拟停车。
- `CHECK_METER`：`linear.x=0.0`，`angular.z=0.0`，模拟暂停并复核仪表检测。
- `NORMAL`：`linear.x=0.1`，`angular.z=0.0`，模拟低速前进。
