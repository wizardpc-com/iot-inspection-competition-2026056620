from pathlib import Path
import zipfile


WORK_ID = "2026056620"
ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / f"{WORK_ID}-参赛总文件夹"

DIRS = [
    SUBMISSION / f"{WORK_ID}-01 作品与答辩材料",
    SUBMISSION / f"{WORK_ID}-02 素材和源码",
    SUBMISSION / f"{WORK_ID}-03 设计和开发文档",
    SUBMISSION / f"{WORK_ID}-04 作品演示视频",
]

REQUIRED = [
    SUBMISSION / "README.txt",
    SUBMISSION / f"{WORK_ID}-提交材料清单.md",
    DIRS[0] / f"{WORK_ID}-答辩PPT内容规划.md",
    DIRS[0] / f"{WORK_ID}-系统架构与运行展示说明.md",
    DIRS[1] / f"{WORK_ID}-素材源码.zip",
    DIRS[1] / "源码说明-readme.txt",
    DIRS[2] / f"{WORK_ID}-作品信息摘要.md",
    DIRS[2] / f"{WORK_ID}-物联网应用类作品技术文档.md",
    DIRS[2] / f"{WORK_ID}-AI工具使用说明.md",
    DIRS[2] / f"{WORK_ID}-测试报告.md",
    DIRS[3] / f"{WORK_ID}-作品演示视频提交说明.md",
]

DISALLOWED_CODEPOINTS = [
    [26410, 23457, 26680],
    [24453, 20154, 24037, 30830, 35748],
    [24453, 22635, 20889],
    [33609, 31295],
    [20869, 37096],
    [19981, 24314, 35758],
    [21442, 32771, 20869, 23481],
    [71, 80, 84],
    [67, 104, 97, 116, 71, 80, 84],
    [67, 111, 100, 101, 120],
    [35762, 31295],
    [21475, 25773],
]


def ok(condition: bool, message: str) -> int:
    print(f"[{'OK' if condition else 'FAIL'}] {message}")
    return 0 if condition else 1


def scan_text() -> int:
    errors = 0
    for path in SUBMISSION.rglob("*"):
        if path.is_file() and path.suffix.lower() not in {".zip", ".pt", ".jpg", ".jpeg", ".png"}:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for item in DISALLOWED_CODEPOINTS:
                term = "".join(chr(codepoint) for codepoint in item)
                if term in content:
                    print(f"[FAIL] unsuitable term in {path}")
                    errors += 1
    return errors


def check_zip() -> int:
    zip_path = DIRS[1] / f"{WORK_ID}-素材源码.zip"
    errors = ok(zip_path.exists(), f"zip exists: {zip_path.name}")
    if not zip_path.exists():
        return errors
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = set(archive.namelist())
    required_entries = [
        "source_package/iot_inspection_ros2_mvp/README.md",
        "source_package/iot_inspection_ros2_mvp/requirements.txt",
        "source_package/iot_inspection_ros2_mvp/ros2_ws/src/inspection_mvp/package.xml",
        "source_package/iot_inspection_ros2_mvp/ros2_ws/src/inspection_mvp/setup.py",
    ]
    for entry in required_entries:
        errors += ok(entry in names, f"zip entry: {entry}")
    return errors


def main() -> None:
    errors = ok(SUBMISSION.exists(), f"submission folder exists: {SUBMISSION.name}")
    for directory in DIRS:
        errors += ok(directory.exists(), f"folder exists: {directory.name}")
        errors += ok((directory / "README.txt").exists(), f"readme exists: {directory.name}")
    for path in REQUIRED:
        errors += ok(path.exists(), f"required file exists: {path.name}")
    errors += check_zip()
    errors += scan_text()
    if errors:
        raise SystemExit(f"Check failed with {errors} issue(s).")
    print("Submission tree is ready for GitHub sharing.")


if __name__ == "__main__":
    main()
