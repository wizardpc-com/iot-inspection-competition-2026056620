# Topic Interface

本系统使用 ROS2 标准消息类型。视觉相关数据通过 `std_msgs/String` 传递 JSON，运动控制接口使用 `geometry_msgs/Twist`。后续新增视觉模块时，建议沿用“订阅 `/inspection/image_path`、发布 `/vision/<module>_result`”的接口形式。

## /inspection/image_path

- 类型：`std_msgs/String`
- 发布者：`image_source_node`
- 订阅者：`crack_detector_node`、`meter_detector_node`
- 作用：发布本地巡检图片路径，模拟机器人采集到图像。

示例：

```json
{
  "station_id": "P001",
  "image_path": "/abs/path/demo_images/test_01.jpg",
  "timestamp": "2026-05-06T10:00:00",
  "source_type": "demo_image"
}
```

## /vision/crack_result

- 类型：`std_msgs/String`
- 发布者：`crack_detector_node`
- 订阅者：`inspection_manager_node`
- 作用：发布裂缝检测结果和标注图路径。

示例：

```json
{
  "station_id": "P001",
  "image_path": "/abs/path/demo_images/crack_01.jpg",
  "annotated_image_path": "/abs/path/outputs/annotated/crack_01_annotated.jpg",
  "detected": true,
  "class_name": "pipe_crack",
  "count": 1,
  "max_conf": 0.84,
  "detections": [
    {
      "bbox": [120.0, 80.0, 260.0, 180.0],
      "conf": 0.84,
      "class_id": 0,
      "class_name": "pipe_crack"
    }
  ],
  "threshold": 0.5,
  "timestamp": "2026-05-06T10:00:02"
}
```

## /vision/meter_result

- 类型：`std_msgs/String`
- 发布者：`meter_detector_node`
- 订阅者：`inspection_manager_node`
- 作用：发布仪表关键部件检测结果、标注图路径和估算读数。

示例：

```json
{
  "station_id": "P001",
  "image_path": "/abs/path/demo_images/meter_01.jpg",
  "annotated_image_path": "/abs/path/outputs/meter_annotated/meter_01_annotated.jpg",
  "annotated_save_ok": true,
  "meter_output_dir": "/abs/path/outputs/meter_annotated",
  "detected": true,
  "detector_type": "meter_keypart_detector",
  "model_backend": "yolov5_detect_py",
  "count": 4,
  "class_counts": {"base": 1, "start": 1, "end": 1, "tip": 1},
  "max_conf": 0.91,
  "detections": [
    {
      "bbox": [190.0, 180.0, 230.0, 220.0],
      "conf": 0.93,
      "class_id": 0,
      "class_name": "base"
    }
  ],
  "meter_status": "structure_detected",
  "reading_status": "estimated",
  "reading_value": 53.2,
  "reading_unit": "unit",
  "reading_ratio": 0.532,
  "reading_method": "keypart_angle_linear_scale",
  "reading_reason": "start_angle=180.00,end_angle=0.00,tip_angle=84.24,direction=clockwise",
  "reason": "detected_required_meter_parts=4/4",
  "threshold": 0.5,
  "timestamp": "2026-05-06T10:00:03",
  "error": null
}
```

## /inspection/state

- 类型：`std_msgs/String`
- 发布者：`inspection_manager_node`
- 订阅者：展示端或记录端
- 作用：发布当前巡检汇总状态。节点会定时发布最新状态；未收到图片和视觉结果时状态为 `IDLE`。

示例：

```json
{
  "state": "NORMAL",
  "station_id": "P001",
  "reason": "crack_result_received",
  "suggested_action": "continue_forward_demo",
  "motion_policy": "always_forward_in_current_demo",
  "timestamp": "2026-05-06T10:00:04"
}
```

## /inspection/report

- 类型：`std_msgs/String`
- 发布者：`inspection_manager_node`
- 作用：发布适合录屏展示的人类可读巡检报告，包含裂缝检测摘要、仪表检测摘要、估算读数和当前演示动作。

## /cmd_vel

- 类型：`geometry_msgs/Twist`
- 发布者：`inspection_manager_node`
- 订阅者：`fake_base_node`
- 作用：模拟小车运动控制接口。当前版本假设小车持续前进，因此 `linear.x` 持续为配置的小速度，默认 `0.1`。
