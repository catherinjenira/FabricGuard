
from pathlib import Path
from collections import Counter
import yaml

DATA_YAML = Path(
    r"Febric Defect Detection and Segm.yolov/data.yaml"
)

with open(DATA_YAML, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

names = config["names"]

print("\n========== FABRICGUARD DATASET CHECK ==========")

for split in ["train", "val", "test"]:

    image_dir = (DATA_YAML.parent / config[split]).resolve()
    label_dir = image_dir.parent / "labels"

    print(f"\n--- {split.upper()} ---")

    if not image_dir.exists():
        print("Image folder not found:", image_dir)
        continue

    images = [
        p for p in image_dir.iterdir()
        if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
    ]

    print("Total images:", len(images))

    counts = Counter()
    missing = 0
    invalid = 0

    for img in images:
        label = label_dir / f"{img.stem}.txt"

        if not label.exists():
            missing += 1
            continue

        for line in label.read_text().splitlines():
            if not line.strip():
                continue

            parts = line.split()

            try:
                class_id = int(parts[0])
                coords = [float(x) for x in parts[1:]]

                if (
                    class_id < 0 or class_id >= len(names)
                    or len(coords) < 6
                    or len(coords) % 2 != 0
                    or not all(0 <= x <= 1 for x in coords)
                ):
                    invalid += 1
                    continue

                counts[class_id] += 1

            except ValueError:
                invalid += 1

    print("Missing labels:", missing)
    print("Invalid annotations:", invalid)

    for i, name in enumerate(names):
        print(f"{name}: {counts[i]} annotations")

print("\n========== CHECK COMPLETED ==========")
