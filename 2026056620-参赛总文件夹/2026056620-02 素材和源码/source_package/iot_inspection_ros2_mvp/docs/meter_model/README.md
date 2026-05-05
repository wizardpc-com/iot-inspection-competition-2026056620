# Meter Key-Part Model

This directory documents the meter key-part detection and reading-estimation branch.

Model placement:

```text
iot_inspection_ros2_mvp/models/meter_best.pt
```

Optional last checkpoint:

```text
iot_inspection_ros2_mvp/models/meter_last.pt
```

Known model information:

- Base model: YOLOv5s
- Training: 100 epochs
- Sample mAP: 0.869
- Current capability: detect meter area and key parts such as pointer and scale regions
- Current ROS2 integration: publish detection boxes, confidence values, annotated image path, and estimated reading on `/vision/meter_result`

Original command reference:

```bash
python detect.py --weights best.pt --source <image_path> --save-txt --save-conf
```

Reading estimation uses detected `base`, `start`, `end`, and `tip` key parts. The computed pointer ratio is mapped to the configured range in `config/demo.yaml`.
