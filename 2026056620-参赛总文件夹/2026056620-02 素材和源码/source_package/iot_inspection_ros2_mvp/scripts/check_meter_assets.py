from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    ROOT / "models" / "meter_best.pt",
    ROOT / "docs" / "meter_model" / "README.md",
]

OPTIONAL = [
    ROOT / "models" / "meter_last.pt",
]


def main():
    ok = True
    print("Meter asset check")
    for path in REQUIRED:
        exists = path.exists()
        print(f"[{'OK' if exists else 'MISSING'}] required: {path}")
        ok = ok and exists
    for path in OPTIONAL:
        exists = path.exists()
        print(f"[{'OK' if exists else 'SKIP'}] optional: {path}")
    if not ok:
        raise SystemExit("Missing required meter assets.")
    print("Meter assets are ready.")


if __name__ == "__main__":
    main()
