# Models

本目录只保留当前运行最需要的模型文件和 YOLOv5 仪表运行入口：

- `crack_best.pt`：裂缝检测模型。
- `meter_best.pt`：仪表关键部件检测模型，当前为 YOLOv5 旧格式权重。
- `yolov5/`：YOLOv5 官方工程目录，用于运行 `meter_best.pt`。

模型路径可在 `ros2_ws/src/inspection_mvp/config/demo.yaml` 中配置。裂缝模型通过 `ultralytics.YOLO` 加载，仪表模型通过本地 YOLOv5 `detect.py` 推理。
