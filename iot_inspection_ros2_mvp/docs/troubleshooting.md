# Troubleshooting

## 1. `ros2 launch` 找不到包

确认已经构建并 source：

```bash
source /opt/ros/humble/setup.bash
cd iot_inspection_ros2_mvp/ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

## 2. `/inspection/image_path` 没有输出

检查 `demo_images/` 中是否有 `.jpg`、`.jpeg`、`.png` 图片。目录为空时 `image_source_node` 会打印提示，但节点不会崩溃。

## 3. 裂缝模型无法加载

检查模型路径：

```text
iot_inspection_ros2_mvp/models/crack_best.pt
```

如果文件名或位置不同，请修改：

```text
iot_inspection_ros2_mvp/ros2_ws/src/inspection_mvp/config/demo.yaml
```

## 4. 仪表模型无法加载

检查模型路径：

```text
iot_inspection_ros2_mvp/models/meter_best.pt
```

当前仪表节点使用本地 YOLOv5 `detect.py` 调用 `meter_best.pt`。如果 `/vision/meter_result` 中出现 `meter_yolov5_backend_unavailable`，说明模型文件或 YOLOv5 推理入口没有放好。处理方式：

- 确认 `meter_best.pt` 已放在 `models/` 下。
- 确认 YOLOv5 工程已放在 `models/yolov5/` 下，且存在 `models/yolov5/detect.py`。
- 确认 WSL/Ubuntu 环境已安装 YOLOv5 依赖、`torch`、`opencv-python`。
- 运行单节点测试脚本定位问题：

```bash
cd iot_inspection_ros2_mvp
python3 scripts/test_meter_node.py --image demo_images/你的仪表图片.jpg
```

如果脚本仍无法运行，优先查看 YOLOv5 `detect.py` 的 stderr 输出，通常是 YOLOv5 依赖缺失、权重路径错误或类别名称配置不匹配。

## 5. `outputs/meter_annotated/` 没有结果图

先查看 `/vision/meter_result`：

```bash
ros2 topic echo /vision/meter_result --once
```

- `annotated_save_ok=true`：结果图已经保存，查看 `annotated_image_path`。
- `meter_status=error`：优先查看 `error` 字段。
- `count=0`：模型运行了，但当前图片没有检测到符合阈值的仪表关键部件，可降低 `meter_conf_threshold` 或更换仪表图片。

## 6. `/inspection/state` 看起来没有变化

当前管理节点是汇总节点，状态会定时发布。先确认两个视觉结果话题是否有输出：

```bash
ros2 topic echo /vision/crack_result --once
ros2 topic echo /vision/meter_result --once
```

如果视觉节点没有输出，状态会保持 `IDLE`。如果视觉节点有输出，状态会更新为 `NORMAL`，报告中会包含裂缝和仪表摘要。

## 7. `/cmd_vel` 为什么一直前进

这是当前版本的演示策略。比赛录屏阶段先展示模型调用和 ROS2 通信，暂时不做“检测到裂缝后停车”的控制逻辑。真实底盘接入后，可以在 `inspection_manager_node` 中按需要修改运动策略。
