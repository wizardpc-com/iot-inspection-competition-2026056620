# Troubleshooting

## Package not found

现象：

```text
Package 'inspection_mvp' not found
```

处理：

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
ros2 pkg list | grep inspection_mvp
```

## Model file not found

现象：

```text
YOLO model file not found
```

处理：

确认模型放在：

```text
iot_inspection_ros2_mvp/models/best.pt
```

如果模型放在其他位置，修改：

```text
ros2_ws/src/inspection_mvp/config/demo.yaml
```

## No demo images found

现象：

```text
No demo images found
```

处理：

确认图片放在：

```text
iot_inspection_ros2_mvp/demo_images/
```

支持格式：

- `.jpg`
- `.jpeg`
- `.png`

## Ultralytics import failed

现象：

```text
Failed to load YOLO model
```

处理：

```bash
cd iot_inspection_ros2_mvp
python3 -m pip install -r requirements.txt
```

如果机器没有 GPU，也可以使用 CPU 推理，只是速度会慢一些。

## No annotated image generated

可能原因：

- 模型未加载成功
- 图片路径不存在
- 输出目录没有权限

处理：

确认 `outputs/annotated/` 可以创建，或在 `demo.yaml` 中修改 `output_dir`。

## rqt_graph not available

处理：

```bash
sudo apt install ros-humble-rqt-graph
rqt_graph
```

## Launch 后路径不对

默认配置使用相对于 `ros2_ws` 的路径。建议按以下方式运行：

```bash
cd iot_inspection_ros2_mvp/ros2_ws
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

如果必须从其他目录运行，请用绝对路径覆盖参数或修改 `demo.yaml`。
