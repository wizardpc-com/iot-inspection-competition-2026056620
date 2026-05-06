# YOLOv5 Compatibility Runtime

本目录用于放置 YOLOv5 官方工程，使旧格式仪表权重 `models/meter_best.pt` 可以通过 `detect.py` 推理。

需要保证以下文件存在：

```text
models/yolov5/detect.py
models/yolov5/models/yolo.py
models/yolov5/utils/
```

推荐放置方式：

```bash
cd iot_inspection_ros2_mvp/models
git clone https://github.com/ultralytics/yolov5.git yolov5
cd yolov5
python3 -m pip install -r requirements.txt
```

当前 ROS2 仪表节点会调用：

```bash
python3 models/yolov5/detect.py --weights models/meter_best.pt --source <image> --save-txt --save-conf
```

推理生成的图片和 txt 会被解析后发布到 `/vision/meter_result`。
