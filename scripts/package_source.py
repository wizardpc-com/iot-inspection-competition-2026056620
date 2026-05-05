from pathlib import Path
import zipfile


WORK_ID = "2026056620"
ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / f"{WORK_ID}-参赛总文件夹"
DIR_02 = SUBMISSION / f"{WORK_ID}-02 素材和源码"
SOURCE_PACKAGE = DIR_02 / "source_package"
ZIP_PATH = DIR_02 / f"{WORK_ID}-素材源码.zip"

EXCLUDE_DIRS = {"build", "install", "log", "__pycache__", ".git", ".vscode", ".idea"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".tmp", ".cache"}


def excluded(path: Path) -> bool:
    return bool(set(path.parts) & EXCLUDE_DIRS) or path.suffix.lower() in EXCLUDE_SUFFIXES


def main() -> None:
    if not SOURCE_PACKAGE.exists():
        raise SystemExit("source_package does not exist. Run create_submission_workspace.py first.")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    count = 0
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE_PACKAGE.rglob("*")):
            relative = path.relative_to(SOURCE_PACKAGE)
            if path.is_file() and not excluded(relative):
                archive.write(path, path.relative_to(DIR_02).as_posix())
                count += 1
    print(f"Created {ZIP_PATH}")
    print(f"Packaged files: {count}")


if __name__ == "__main__":
    main()
