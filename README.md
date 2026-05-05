# 电力场景下的智能机器人巡检系统

作品编号：2026056620  
作品类别：物联网应用 - 行业应用

本仓库用于中国大学生计算机设计大赛物联网应用类作品的版本管理与材料交付。当前版本为 ROS2 仿真系统与电力场景 AI 视觉识别原型，已完成“图像输入 → AI裂缝识别 → ROS2结果发布 → 巡检状态判断 → 模拟运动反馈 → 结果保存”的核心闭环。

## 仓库结构

```text
iot_inspection_ros2_mvp/        ROS2 Python MVP 源码
model_reference/                模型训练与原始推理流程参考文件
scripts/                        提交材料生成、打包、检查脚本
2026056620-参赛总文件夹/        面向评审和队友共享的参赛材料
```

## 运行 ROS2 MVP

```bash
cd iot_inspection_ros2_mvp
python3 -m pip install -r requirements.txt

source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build
source install/setup.bash
ros2 launch inspection_mvp inspection_demo.launch.py
```

常用话题查看：

```bash
ros2 topic list
ros2 topic echo /vision/crack_result --once
ros2 topic echo /inspection/state --once
ros2 topic echo /inspection/report --once
```

## 生成参赛材料

```bash
python scripts/create_submission_workspace.py
python scripts/package_source.py
python scripts/check_submission_tree.py
```

生成的参赛材料位于 `2026056620-参赛总文件夹/`。

## GitHub 远程仓库

```bash
git remote add origin https://github.com/wizardpc-com/iot-inspection-competition-2026056620.git
```

当前仓库不包含真实小车、真实摄像头、K230实机部署、激光雷达SLAM、无人机、机械臂或完整空地协同实现；这些内容作为后续扩展方向保留。
