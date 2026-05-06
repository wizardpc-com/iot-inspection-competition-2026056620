from pathlib import Path
import os
import shutil
import textwrap


WORK_ID = "2026056620"
WORK_NAME = "电力场景下的智能机器人巡检系统"
CATEGORY = "物联网应用 - 行业应用"

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / f"{WORK_ID}-参赛总文件夹"
SOURCE_PROJECT = ROOT / "iot_inspection_ros2_mvp"

DIR_01 = SUBMISSION / f"{WORK_ID}-01 作品与答辩材料"
DIR_02 = SUBMISSION / f"{WORK_ID}-02 素材和源码"
DIR_03 = SUBMISSION / f"{WORK_ID}-03 设计和开发文档"
DIR_04 = SUBMISSION / f"{WORK_ID}-04 作品演示视频"


def text(value: str) -> str:
    return textwrap.dedent(value).strip() + "\n"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            os.chmod(path, 0o700)
        except OSError:
            pass
    path.write_text(text(content), encoding="utf-8")


def on_remove_error(function, path, _excinfo) -> None:
    os.chmod(path, 0o700)
    function(path)


def ignore_generated(_dir_name, names):
    ignored = set()
    ignored_names = {
        "build",
        "install",
        "log",
        "__pycache__",
        ".git",
        ".vscode",
        ".idea",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
    for name in names:
        if name in ignored_names or name.lower().endswith((".pyc", ".pyo", ".tmp", ".cache")):
            ignored.add(name)
    return ignored


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists() and src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def sync_source_package() -> None:
    package_root = DIR_02 / "source_package"
    if package_root.exists():
        shutil.rmtree(package_root, onexc=on_remove_error)
    package_root.mkdir(parents=True, exist_ok=True)

    project_dst = package_root / "iot_inspection_ros2_mvp"
    for name in ["README.md", "requirements.txt", ".gitignore"]:
        copy_if_exists(SOURCE_PROJECT / name, project_dst / name)

    for dirname in ["docs", "models", "scripts"]:
        src = SOURCE_PROJECT / dirname
        if src.exists():
            shutil.copytree(src, project_dst / dirname, ignore=ignore_generated)

    demo_dst = project_dst / "demo_images"
    demo_dst.mkdir(parents=True, exist_ok=True)
    copy_if_exists(SOURCE_PROJECT / "demo_images" / "README.md", demo_dst / "README.md")
    write(
        demo_dst / "README.txt",
        "本目录用于放置演示图片。源码包默认不附带大量测试图片，运行前可将裂缝或仪表图片放入本目录。",
    )

    outputs_dst = project_dst / "outputs"
    outputs_dst.mkdir(parents=True, exist_ok=True)
    copy_if_exists(SOURCE_PROJECT / "outputs" / "README.md", outputs_dst / "README.md")
    for output_name, description in [
        ("annotated", "裂缝检测标注图"),
        ("meter_annotated", "仪表关键部件检测标注图"),
    ]:
        dst_dir = outputs_dst / output_name
        dst_dir.mkdir(parents=True, exist_ok=True)
        copy_if_exists(SOURCE_PROJECT / "outputs" / output_name / "README.md", dst_dir / "README.md")
        write(dst_dir / "README.txt", f"本目录保存 ROS2 MVP 运行后生成的{description}。")

    ros_pkg_src = SOURCE_PROJECT / "ros2_ws" / "src" / "inspection_mvp"
    ros_pkg_dst = project_dst / "ros2_ws" / "src" / "inspection_mvp"
    if ros_pkg_src.exists():
        shutil.copytree(ros_pkg_src, ros_pkg_dst, ignore=ignore_generated)

    reference_dst = package_root / "model_reference"
    reference_dst.mkdir(parents=True, exist_ok=True)
    for name in ["data.yaml", "predict.py", "run.py"]:
        copy_if_exists(ROOT / "model_reference" / name, reference_dst / name)
    write(
        reference_dst / "README.txt",
        "本目录保存模型训练与原始推理流程参考文件。当前比赛系统的正式运行入口是 iot_inspection_ros2_mvp/ros2_ws/src/inspection_mvp。",
    )


def write_submission_docs() -> None:
    write(
        SUBMISSION / "README.txt",
        f"""
        {WORK_ID}-参赛总文件夹

        作品名称：{WORK_NAME}
        作品类别：{CATEGORY}

        本目录保存中国大学生计算机设计大赛物联网应用类作品材料。当前作品为 ROS2 仿真系统与电力场景 AI 视觉识别原型，已完成图片输入、裂缝识别、仪表关键部件检测、仪表估算读数、ROS2结果发布、状态汇总、模拟小车持续前进和结果保存。
        """,
    )
    write(DIR_01 / "README.txt", "本目录保存答辩展示相关材料，包括 PPT 内容规划、系统架构说明和展示素材清单。")
    write(DIR_02 / "README.txt", "本目录保存源码包和运行说明。2026056620-素材源码.zip 为提交源码压缩包。")
    write(DIR_03 / "README.txt", "本目录保存设计和开发文档，包括作品信息摘要、技术文档、AI工具使用说明和测试报告。")
    write(DIR_04 / "README.txt", "本目录保存作品演示视频提交说明和素材清单。正式演示视频文件可命名为 2026056620-作品演示视频.mp4。")

    write(
        DIR_01 / f"{WORK_ID}-答辩PPT内容规划.md",
        f"""
        # {WORK_ID}-答辩PPT内容规划

        1. 标题页：作品编号、作品名称、物联网应用 - 行业应用。
        2. 项目背景：电力巡检中管道、设备和仪表状态观察需求。
        3. 场景痛点：人工巡检效率、记录一致性和异常发现问题。
        4. 当前版本目标：完成 ROS2 仿真系统与 AI视觉识别流程。
        5. 系统总体方案：图片输入、裂缝检测、仪表关键部件检测、状态汇总、模拟运动反馈。
        6. ROS2节点架构：image_source_node、crack_detector_node、meter_detector_node、inspection_manager_node、fake_base_node。
        7. 裂缝识别模块：crack_best.pt 接入、/vision/crack_result 输出、结果图保存。
        8. 仪表检测模块：YOLOv5 meter_best.pt 通过 detect.py 接入、/vision/meter_result 输出、估算读数。
        9. 状态汇总与运动接口：/inspection/state、/inspection/report、/cmd_vel。
        10. 运行展示：ros2 launch、topic echo、outputs/annotated、outputs/meter_annotated。
        11. 测试结果：模型加载、图片输入、话题通信、状态汇总、运动反馈、结果保存。
        12. 创新点与扩展：ROS2模块化、AI节点化、双视觉模型接入、真实硬件接口扩展。
        """,
    )
    write(
        DIR_01 / f"{WORK_ID}-系统架构与运行展示说明.md",
        """
        # 系统架构与运行展示说明

        ```text
        image_source_node
            ↓ /inspection/image_path
        crack_detector_node
            ↓ /vision/crack_result
        inspection_manager_node
            ↓ /inspection/state
            ↓ /inspection/report
            ↓ /cmd_vel
        fake_base_node

        image_source_node
            ↓ /inspection/image_path
        meter_detector_node
            ↓ /vision/meter_result
        inspection_manager_node
        ```

        展示重点包括 ros2 launch 启动、ros2 topic list、/vision/crack_result、/vision/meter_result、/inspection/state、/inspection/report、/cmd_vel、fake_base_node 日志以及两个 outputs 目录中的结果图。
        """,
    )
    write(
        DIR_01 / f"{WORK_ID}-答辩展示素材清单.md",
        """
        # 答辩展示素材清单

        - ros2 launch 启动截图或录屏帧。
        - ros2 topic list 截图。
        - /inspection/image_path 输出截图。
        - /vision/crack_result 输出截图。
        - /vision/meter_result 输出截图。
        - /inspection/state 输出截图。
        - /inspection/report 输出截图。
        - /cmd_vel 输出截图。
        - fake_base_node 模拟前进日志截图。
        - outputs/annotated 裂缝标注图。
        - outputs/meter_annotated 仪表标注图。
        - rqt_graph 节点关系图。
        """,
    )

    write(
        DIR_02 / "源码说明-readme.txt",
        """
        源码说明

        当前源码对应 iot_inspection_ros2_mvp，系统不依赖真实摄像头和真实小车，重点验证电力场景下的 ROS2 仿真与 AI视觉识别流程。

        运行步骤：

        ```bash
        cd iot_inspection_ros2_mvp
        python3 -m pip install -r requirements.txt

        source /opt/ros/humble/setup.bash
        cd ros2_ws
        colcon build
        source install/setup.bash
        ros2 launch inspection_mvp inspection_demo.launch.py
        ```

        查看话题：

        ```bash
        ros2 topic list
        ros2 topic echo /vision/crack_result --once
        ros2 topic echo /vision/meter_result --once
        ros2 topic echo /inspection/state --once
        ros2 topic echo /inspection/report --once
        ros2 topic echo /cmd_vel --once
        ```

        裂缝模型放置：iot_inspection_ros2_mvp/models/crack_best.pt
        仪表模型放置：iot_inspection_ros2_mvp/models/meter_best.pt
        YOLOv5 推理入口：iot_inspection_ros2_mvp/models/yolov5/detect.py
        图片放置：iot_inspection_ros2_mvp/demo_images/
        裂缝结果目录：iot_inspection_ros2_mvp/outputs/annotated/
        仪表结果目录：iot_inspection_ros2_mvp/outputs/meter_annotated/
        """,
    )
    write(DIR_02 / "开源组件与版权说明.txt", "本作品使用 ROS2 Humble、rclpy、std_msgs、geometry_msgs、Ultralytics YOLO、torch、OpenCV、NumPy、PyYAML 等开源组件。模型文件、演示图片和视频素材由团队统一管理。")
    write(DIR_02 / "运行环境与依赖说明.txt", "推荐环境：Windows + WSL2 Ubuntu 22.04 或原生 Ubuntu 22.04，ROS2 Humble，Python 3.10。主要依赖：rclpy、std_msgs、geometry_msgs、ament_python、colcon、ultralytics、YOLOv5、torch、opencv-python、numpy、pyyaml。")

    write(
        DIR_03 / f"{WORK_ID}-作品信息摘要.md",
        f"""
        # {WORK_ID}-作品信息摘要

        - 作品编号：{WORK_ID}
        - 作品名称：{WORK_NAME}
        - 作品类别：{CATEGORY}
        - 比赛方向：中国大学生计算机设计大赛物联网应用类相关赛道

        ## 作品简介

        本作品面向电力巡检场景，构建基于 ROS2 的智能巡检原型，实现图片输入、YOLO裂缝识别、仪表关键部件检测、估算读数、状态汇总、模拟运动反馈和结果保存。

        ## 创新描述

        作品将裂缝识别模型和仪表关键部件检测模型节点化接入 ROS2，通过话题机制联通图片输入、AI识别、状态管理和运动接口，并为真实摄像头、真实底盘和边缘部署预留扩展路径。

        ## 当前完成内容

        系统包含 image_source_node、crack_detector_node、meter_detector_node、inspection_manager_node、fake_base_node 等节点，完成 /inspection/image_path、/vision/crack_result、/vision/meter_result、/inspection/state、/inspection/report、/cmd_vel 等关键话题通信。

        ## 团队分工

        | 成员 | 分工 |
        |---|---|
        | 严睿清 | 项目总体方案、ROS2系统架构、节点通信设计、状态汇总、系统集成与材料统筹 |
        | 张昌辉 | 裂缝识别模型、crack_best.pt 模型训练与测试、裂缝检测样例图、模型推理脚本和结果说明 |
        | 刘安祺 | 仪表关键部件检测方向、仪表识别接口方案、电力场景素材和文档整理 |

        ## 开发与运行平台

        Windows + WSL2 Ubuntu 22.04、ROS2 Humble、Python 3.10、Ultralytics YOLO、OpenCV、NumPy、PyYAML。
        """,
    )
    write(
        DIR_03 / f"{WORK_ID}-物联网应用类作品技术文档.md",
        """
        # 物联网应用类作品技术文档

        ## 作品概述

        本作品当前版本聚焦“地面巡检小车 + AI视觉识别 + ROS2通信与任务管理”的最小可运行原型。系统重点验证图片输入、AI裂缝识别、仪表关键部件检测、估算读数、ROS2结果发布、状态汇总、模拟运动反馈和结果保存。

        ## 需求分析

        电力巡检需要对管道裂缝、设备状态和仪表信息进行记录。当前版本使用本地图片模拟巡检输入，通过 YOLO 模型完成管道裂缝识别和仪表关键部件检测，通过 ROS2 话题完成模块解耦和结果汇总。

        ## 技术方案

        - image_source_node 发布 /inspection/image_path。
        - crack_detector_node 加载 models/crack_best.pt，发布 /vision/crack_result。
        - meter_detector_node 通过 models/yolov5/detect.py 调用 models/meter_best.pt，发布 /vision/meter_result。
        - inspection_manager_node 发布 /inspection/state、/inspection/report、/cmd_vel。
        - fake_base_node 订阅 /cmd_vel 并模拟小车持续前进。

        ## 状态与运动策略

        当前版本先聚焦模型调用与 ROS2 通信验证，假设小车持续前进。/cmd_vel 默认发布 linear.x=0.1。后续接入真实底盘后，可在 inspection_manager_node 中扩展停车、绕行、复核等策略。

        ## 当前边界与扩展

        当前版本为 ROS2 仿真系统与 AI视觉识别原型。真实小车底盘、真实摄像头、K230边缘部署、激光雷达定位、路径规划和空地协同属于后续扩展方向。
        """,
    )
    write(
        DIR_03 / f"{WORK_ID}-AI工具使用说明.md",
        """
        # AI工具使用说明

        本作品材料整理阶段使用 DeepSeek、豆包、即梦AI 辅助进行资料结构整理、语言润色和展示素材构思。团队负责系统实现、模型运行、ROS2测试、结果截图、视频录制和最终材料选择。

        | 工具 | 使用环节 | 作用 |
        |---|---|---|
        | DeepSeek | 文档整理 | 技术路线梳理、文档表达优化 |
        | 豆包 | 展示材料 | 摘要、图表说明和展示文案润色 |
        | 即梦AI | 视觉素材 | 展示封面或示意图风格构思 |

        AI工具用于辅助表达和材料组织，不替代系统实现、运行验证和团队判断。
        """,
    )
    write(
        DIR_03 / f"{WORK_ID}-测试报告.md",
        """
        # 测试报告

        | 编号 | 测试项 | 测试方法 | 结果 |
        |---|---|---|---|
        | T01 | 裂缝模型加载测试 | 启动 crack_detector_node | crack_best.pt 在节点启动时加载 |
        | T02 | 仪表模型入口测试 | 启动 meter_detector_node | detect.py 与 meter_best.pt 路径可被节点检查 |
        | T03 | 图片输入测试 | echo /inspection/image_path | image_source_node 发布图片路径 JSON |
        | T04 | 裂缝识别测试 | echo /vision/crack_result | 输出 detected、bbox、conf、max_conf、annotated_image_path |
        | T05 | 仪表检测测试 | echo /vision/meter_result | 输出 class_counts、reading_status、reading_value、annotated_image_path |
        | T06 | ROS2话题通信测试 | ros2 topic list | 关键节点与话题可见 |
        | T07 | 状态汇总测试 | echo /inspection/state | 系统输出 IDLE 或 NORMAL |
        | T08 | 运动反馈接口测试 | echo /cmd_vel | 当前版本持续发布小速度前进 |
        | T09 | 结果图保存测试 | 查看 outputs/annotated 与 outputs/meter_annotated | 生成带检测框的结果图 |

        测试结论：当前 ROS2 仿真系统完成图片输入、裂缝识别、仪表关键部件检测、估算读数、状态汇总、模拟运动反馈和结果图保存流程。
        """,
    )

    write(DIR_04 / f"{WORK_ID}-作品演示视频提交说明.md", "演示视频建议为 MP4，时长 5-8 分钟，展示项目背景、系统方案、ROS2节点架构、ros2 launch 启动、裂缝识别结果、仪表检测结果、topic echo、模拟小车前进和结果图保存。")
    write(DIR_04 / f"{WORK_ID}-演示视频素材清单.md", "素材包括 colcon build 成功录屏、ros2 launch 启动录屏、ros2 topic list、/vision/crack_result、/vision/meter_result、/inspection/state、/inspection/report、/cmd_vel、outputs/annotated、outputs/meter_annotated 和系统节点架构图。")
    write(SUBMISSION / f"{WORK_ID}-提交材料清单.md", "提交材料包括 01 作品与答辩材料、02 素材和源码、03 设计和开发文档、04 作品演示视频。源码包为 2026056620-02 素材和源码/2026056620-素材源码.zip。")


def main() -> None:
    for directory in [DIR_01, DIR_02, DIR_03, DIR_04]:
        directory.mkdir(parents=True, exist_ok=True)
    write_submission_docs()
    sync_source_package()
    print(f"Submission folder ready: {SUBMISSION}")


if __name__ == "__main__":
    main()
