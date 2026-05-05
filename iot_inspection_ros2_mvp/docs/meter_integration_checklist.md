# Meter Integration Checklist

## Files To Check

- `models/crack_best.pt`
- `models/meter_best.pt`
- `ros2_ws/src/inspection_mvp/inspection_mvp/meter_detector_node.py`
- `ros2_ws/src/inspection_mvp/inspection_mvp/meter_stub_node.py`
- `ros2_ws/src/inspection_mvp/launch/inspection_demo.launch.py`
- `ros2_ws/src/inspection_mvp/config/demo.yaml`
- `outputs/meter_annotated/`

## Commands To Run

Check model assets:

```bash
cd iot_inspection_ros2_mvp
python scripts/check_meter_assets.py
```

Build ROS2 package:

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
```

Run default compatible mode:

```bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

Run real meter detection and reading mode:

```bash
ros2 launch inspection_mvp inspection_demo.launch.py use_meter_stub:=false
```

Watch meter output:

```bash
ros2 topic echo /vision/meter_result
```

Standalone meter model test:

```bash
cd iot_inspection_ros2_mvp
python scripts/test_meter_node.py --image demo_images/crack_1.jpg --model models/meter_best.pt
```

## Successful Logs

Default mode should show:

```text
Meter stub ready
Published meter stub
```

Real meter mode should show:

```text
Meter key-part model loaded with ultralytics
Received meter inspection image
Meter annotated result saved
Published meter result
```

Successful reading output should include:

```json
{
  "reading_status": "estimated",
  "reading_value": 63.25,
  "reading_ratio": 0.6325,
  "reading_method": "keypart_angle_linear_scale"
}
```

## Expected Boundaries

- Crack detection remains available in both meter modes.
- `meter_stub_node` remains available as fallback.
- `meter_detector_node` detects meter structure and key parts.
- Reading is estimated from key-part geometry and configurable meter range.
