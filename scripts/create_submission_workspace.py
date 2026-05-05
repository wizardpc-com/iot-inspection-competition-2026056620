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

    for dirname in ["docs", "demo_images", "models", "scripts"]:
        src = SOURCE_PROJECT / dirname
        if src.exists():
            shutil.copytree(src, project_dst / dirname, ignore=ignore_generated)

    outputs_dst = project_dst / "outputs"
    outputs_dst.mkdir(parents=True, exist_ok=True)
    copy_if_exists(SOURCE_PROJECT / "outputs" / "README.md", outputs_dst / "README.md")
    for output_name, description in [
        ("annotated", "裂缝检测标注图"),
        ("meter_annotated", "仪表关键部件检测标注图"),
    ]:
        dst_dir = outputs_dst / output_name
        dst_dir.mkdir(parents=True, exist_ok=True)
        src_dir = SOURCE_PROJECT / "outputs" / output_name
        copy_if_exists(src_dir / "README.md", dst_dir / "README.md")
        if src_dir.exists():
            copied = 0
            for item in sorted(src_dir.iterdir()):
                if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                    shutil.copy2(item, dst_dir / item.name)
                    copied += 1
                    if copied >= 5:
                        break
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
        """
        本目录保存模型训练与原始推理流程参考文件。当前比赛系统的正式运行入口是 iot_inspection_ros2_mvp/ros2_ws/src/inspection_mvp。
        """,
    )


def write_submission_docs() -> None:
    write(
        SUBMISSION / "README.txt",
        f"""
        {WORK_ID}-参赛总文件夹

        作品名称：{WORK_NAME}
        作品类别：{CATEGORY}

        本目录保存中国大学生计算机设计大赛物联网应用类作品材料。当前作品为 ROS2 仿真系统与电力场景 AI 视觉识别原型，已完成图像输入、裂缝识别、仪表关键部件检测接入、ROS2结果发布、巡检状态判断、模拟运动反馈和结果保存的核心闭环。
        """,
    )
    write(
        DIR_01 / "README.txt",
        """
        本目录保存答辩展示相关材料，包括 PPT 内容规划、系统架构说明和展示素材清单。正式答辩 PPT 可基于本目录内容制作。
        """,
    )
    write(
        DIR_02 / "README.txt",
        """
        本目录保存源码包和运行说明。2026056620-素材源码.zip 为提交源码压缩包，source_package 为压缩包生成目录。
        """,
    )
    write(
        DIR_03 / "README.txt",
        """
        本目录保存设计和开发文档，包括作品信息摘要、技术文档、AI工具使用说明和测试报告。
        """,
    )
    write(
        DIR_04 / "README.txt",
        """
        本目录保存作品演示视频提交说明和素材清单。正式演示视频文件可命名为 2026056620-作品演示视频.mp4。
        """,
    )

    write(
        DIR_01 / f"{WORK_ID}-答辩PPT内容规划.md",
        f"""
        # {WORK_ID}-答辩PPT内容规划

        1. 标题页：作品编号、作品名称、物联网应用 - 行业应用。
        2. 项目背景：电力巡检中管道、设备和仪表状态监测需求。
        3. 场景痛点：人工巡检效率、记录一致性和异常响应问题。
        4. 当前版本目标：完成 ROS2 仿真系统与 AI视觉识别闭环。
        5. 系统总体方案：图像输入、裂缝识别、仪表关键部件检测、状态管理、模拟运动反馈。
        6. ROS2节点架构：image_source_node、crack_detector_node、meter_detector_node、meter_stub_node、inspection_manager_node、fake_base_node。
        7. 裂缝识别模块：crack_best.pt 接入、/vision/crack_result 输出、结果图保存。
        8. 仪表检测模块：meter_best.pt 接入、/vision/meter_result 输出、读数换算后续扩展。
        9. 巡检状态管理：NORMAL / ALERT / CHECK_METER 规则和 /cmd_vel 指令。
        10. 运行展示：ros2 launch、topic echo、outputs/annotated、outputs/meter_annotated。
        11. 测试结果：模型加载、图片输入、话题通信、状态判断、运动反馈、结果保存。
        12. 创新点与扩展：ROS2模块化、AI节点化、双视觉分支接入、真实硬件接口扩展。
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

        meter_stub_node 或 meter_detector_node
            ↓ /vision/meter_result
        inspection_manager_node
        ```

        展示重点包括 ros2 launch 启动、ros2 topic list、/vision/crack_result、/inspection/state、/inspection/report、/cmd_vel、fake_base_node 日志以及 outputs/annotated 结果图。
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
        - /inspection/state 输出截图。
        - /inspection/report 输出截图。
        - /cmd_vel 输出截图。
        - fake_base_node 模拟停止日志截图。
        - outputs/annotated 带框结果图。
        - rqt_graph 节点关系图。
        """,
    )

    write(
        DIR_02 / "源码说明-readme.txt",
        """
        源码说明

        当前源码对应 iot_inspection_ros2_mvp，系统不依赖真实摄像头和真实小车，重点验证电力场景下的 ROS2 仿真与 AI视觉识别闭环。

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
        ros2 topic echo /inspection/state --once
        ros2 topic echo /inspection/report --once
        ```

        裂缝模型放置：iot_inspection_ros2_mvp/models/crack_best.pt
        仪表模型放置：iot_inspection_ros2_mvp/models/meter_best.pt
        图片放置：iot_inspection_ros2_mvp/demo_images/
        结果目录：iot_inspection_ros2_mvp/outputs/annotated/
        """,
    )
    write(
        DIR_02 / "开源组件与版权说明.txt",
        """
        开源组件与版权说明

        本作品使用 ROS2 Humble、rclpy、std_msgs、geometry_msgs、Ultralytics YOLO、torch、OpenCV、NumPy、PyYAML 等开源组件。crack_best.pt、meter_best.pt、demo_images 图片和演示视频素材由团队统一管理，用于本作品演示和评审材料。
        """,
    )
    write(
        DIR_02 / "运行环境与依赖说明.txt",
        """
        运行环境与依赖说明

        推荐环境：Windows + WSL2 Ubuntu 22.04 或原生 Ubuntu 22.04，ROS2 Humble，Python 3.10。

        主要依赖：rclpy、std_msgs、geometry_msgs、ament_python、colcon、ultralytics、torch、opencv-python、numpy、pyyaml。
        """,
    )

    write(
        DIR_03 / f"{WORK_ID}-作品信息摘要.md",
        f"""
        # {WORK_ID}-作品信息摘要

        - 作品编号：{WORK_ID}
        - 作品名称：{WORK_NAME}
        - 作品类别：{CATEGORY}
        - 比赛方向：中国大学生计算机设计大赛物联网应用类相关赛道

        ## 作品简介

        本作品面向电力巡检场景，构建基于 ROS2 的智能巡检原型，实现图片输入、YOLO裂缝识别、仪表关键部件检测、巡检状态判断、模拟运动反馈和结果保存的闭环验证。

        ## 创新描述

        作品将裂缝识别模型和仪表关键部件检测模型节点化接入 ROS2，通过话题机制联通图像输入、AI识别、状态管理和运动反馈，并为仪表读数换算、真实底盘和边缘部署预留接口。

        ## 当前完成内容

        系统包含 image_source_node、crack_detector_node、meter_detector_node、meter_stub_node、inspection_manager_node、fake_base_node 等节点，完成 /inspection/image_path、/vision/crack_result、/vision/meter_result、/inspection/state、/inspection/report、/cmd_vel 等关键话题通信。

        ## 团队分工

        | 成员 | 分工 |
        |---|---|
        | 严睿清 | 项目总体方案、ROS2系统架构、节点通信设计、巡检任务状态管理、系统集成与材料统筹 |
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

        本作品当前版本聚焦“地面巡检小车 + AI视觉识别 + ROS2通信与任务管理”的最小可运行原型。系统重点验证图像输入、AI裂缝识别、仪表关键部件检测、ROS2结果发布、巡检状态判断、模拟运动反馈和结果保存。

        ## 需求分析

        电力巡检需要对管道裂缝、设备状态和仪表信息进行记录。当前版本使用本地图片模拟巡检输入，通过 YOLO 模型完成管道裂缝识别和仪表关键部件检测，通过 ROS2 话题完成模块解耦和状态反馈。

        ## 技术方案

        - image_source_node 发布 /inspection/image_path。
        - crack_detector_node 加载 models/crack_best.pt，发布 /vision/crack_result。
        - inspection_manager_node 发布 /inspection/state、/inspection/report、/cmd_vel。
        - fake_base_node 订阅 /cmd_vel 并模拟小车前进或停止。
        - meter_stub_node 默认发布 /vision/meter_result，提供兼容演示模式。
        - meter_detector_node 可加载 meter_best.pt，发布仪表关键部件检测结果。

        ## 裂缝识别节点

        crack_detector_node 在启动时加载 crack_best.pt，收到图片路径后调用 Ultralytics YOLO 推理，输出 detected、bbox、conf、class_name、annotated_image_path 等字段，并将标注图保存到 outputs/annotated。

        ## 仪表关键部件检测节点

        meter_detector_node 在 use_meter_stub:=false 时启动，加载 meter_best.pt 并检测仪表盘区域、指针、刻度等关键部件。节点发布 /vision/meter_result，并将结果图保存到 outputs/meter_annotated。当前读数基于 base/start/end/tip 检测框中心点与配置量程进行估算。

        ## 状态判断逻辑

        inspection_manager_node 保持裂缝优先逻辑。检测到裂缝且置信度达到阈值时进入 ALERT，并通过 /cmd_vel 发布停止指令；若仪表关键部件检测结果为 error 或 needs_review，则进入 CHECK_METER；其他情况为 NORMAL。

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
        | T01 | 模型加载测试 | 启动 crack_detector_node | crack_best.pt 在节点启动时加载 |
        | T02 | 图片输入测试 | echo /inspection/image_path | image_source_node 发布图片路径 JSON |
        | T03 | 裂缝识别测试 | echo /vision/crack_result | 输出 detected、bbox、conf、max_conf、annotated_image_path |
        | T04 | ROS2话题通信测试 | ros2 topic list | 关键节点与话题可见 |
        | T05 | 巡检状态判断测试 | echo /inspection/state | 系统输出 NORMAL 或 ALERT |
        | T06 | 运动反馈接口测试 | echo /cmd_vel | ALERT 时发布零速度停止指令 |
        | T07 | 结果图保存测试 | 查看 outputs/annotated | 生成带检测框的结果图 |
        | T08 | 仪表兼容模式测试 | echo /vision/meter_result | meter_stub_node 发布兼容仪表结果 |
        | T09 | 仪表检测分支测试 | use_meter_stub:=false 后 echo /vision/meter_result | meter_detector_node 发布仪表关键部件检测结果 |

        测试结论：当前 ROS2 仿真系统完成图像输入、裂缝识别、仪表关键部件检测接入、状态判断、模拟运动反馈和结果图保存闭环。
        """,
    )

    write(
        DIR_04 / f"{WORK_ID}-作品演示视频提交说明.md",
        """
        # 作品演示视频提交说明

        演示视频建议为 MP4，时长 5-8 分钟，展示项目背景、系统方案、ROS2节点架构、ros2 launch 启动、裂缝识别结果、仪表关键部件检测结果、topic echo、ALERT 状态、CHECK_METER 状态、模拟小车停止和结果图保存。

        视频展示内容以当前 ROS2 仿真系统和 AI视觉识别原型为准。仪表分支当前完成关键部件检测接入，读数换算作为后续扩展方向展示。
        """,
    )
    write(
        DIR_04 / f"{WORK_ID}-演示视频素材清单.md",
        """
        # 演示视频素材清单

        - colcon build 成功录屏。
        - ros2 launch 启动录屏。
        - ros2 topic list 截图。
        - /vision/crack_result 输出截图。
        - /vision/meter_result 输出截图。
        - /inspection/state 输出截图。
        - /inspection/report 输出截图。
        - /cmd_vel 输出截图。
        - fake_base_node 模拟停止日志截图。
        - demo_images 原图。
        - outputs/annotated 带框结果图。
        - outputs/meter_annotated 仪表关键部件检测结果图。
        - 系统节点架构图。
        """,
    )

    write(
        SUBMISSION / f"{WORK_ID}-提交材料清单.md",
        """
        # 提交材料清单

        - 2026056620-01 作品与答辩材料
        - 2026056620-02 素材和源码
        - 2026056620-03 设计和开发文档
        - 2026056620-04 作品演示视频

        源码包：2026056620-02 素材和源码/2026056620-素材源码.zip
        """,
    )


def main() -> None:
    for directory in [DIR_01, DIR_02, DIR_03, DIR_04]:
        directory.mkdir(parents=True, exist_ok=True)
    write_submission_docs()
    sync_source_package()
    print(f"Submission folder ready: {SUBMISSION}")


if __name__ == "__main__":
    main()
