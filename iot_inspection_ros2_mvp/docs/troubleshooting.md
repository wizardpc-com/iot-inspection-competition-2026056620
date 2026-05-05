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
```

## 裂缝模型不存在

确认裂缝模型位于：

```text
iot_inspection_ros2_mvp/models/crack_best.pt
```

## 仪表模型不存在

默认 launch 使用 `meter_stub_node`，不会因为仪表模型缺失影响裂缝检测闭环。启用真实仪表分支前，请确认模型位于：

```text
iot_inspection_ros2_mvp/models/meter_best.pt
```

启用真实仪表分支：

```bash
ros2 launch inspection_mvp inspection_demo.launch.py use_meter_stub:=false
```

## 仪表模型无法被 ultralytics 加载

节点会发布 `/vision/meter_result`，其中 `meter_status=error`、`reading_status=error`。裂缝检测闭环仍可继续运行。可使用原 YOLOv5 命令验证模型文件来源：

```bash
python detect.py --weights best.pt --source 图片路径 --save-txt --save-conf
```

## 图片目录为空

把 `.jpg/.jpeg/.png` 图片放入：

```text
iot_inspection_ros2_mvp/demo_images/
```

## 没有生成仪表结果图

检查：

- 是否使用 `use_meter_stub:=false` 启动。
- `models/meter_best.pt` 是否存在。
- `/vision/meter_result` 是否包含 `error` 字段。
- `meter_output_dir` 是否配置为 `../outputs/meter_annotated`。

## 读数需要复核

当前读数依赖 `base/start/end/tip` 四类关键部件。若关键部件缺失，`reading_status` 会显示 `needs_key_parts`，`reading_value` 为 `null`。处理方式是检查图片质量、模型输出类别、`meter_required_classes` 配置和量程参数。

## 读数方向不符合预期

调整配置：

```yaml
meter_angle_direction: "clockwise"
```

或：

```yaml
meter_angle_direction: "counterclockwise"
```

## 读数量程不符合实际仪表

调整配置：

```yaml
meter_min_value: 0.0
meter_max_value: 100.0
meter_unit: "unit"
```
