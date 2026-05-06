# Meter Integration Checklist

## 文件检查

- `models/meter_best.pt` 存在。
- `models/yolov5/detect.py` 存在。
- `demo_images/` 中有仪表测试图片。
- `outputs/meter_annotated/` 存在。
- `ros2_ws/src/inspection_mvp/config/demo.yaml` 中 `meter_model_path` 指向 `../models/meter_best.pt`。
- `ros2_ws/src/inspection_mvp/config/demo.yaml` 中 `meter_yolov5_detect_script` 指向 `../models/yolov5/detect.py`。

## 单独测试仪表模型

```bash
cd iot_inspection_ros2_mvp
python3 scripts/check_meter_assets.py
python3 scripts/test_meter_node.py --image demo_images/你的仪表图片.jpg
```

成功时应看到 JSON 输出，包含 `detections`、`reading_status`、`reading_value` 和 `annotated_image_path`。

## ROS2 联调

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

另开终端查看：

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
source install/setup.bash
ros2 topic echo /vision/meter_result --once
```

成功时应看到：

- `model_backend=yolov5_detect_py`
- `annotated_save_ok=true`
- `meter_status=structure_detected` 或 `needs_review`
- `annotated_image_path` 指向 `outputs/meter_annotated/` 下的图片
