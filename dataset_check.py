
from pathlib import Path
from collections import Counter
import yaml

yaml_path = Path(
    r"Febric Defect Detection and Segm.yolov\data.yaml"
)

with open(yaml_path, "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)

print("===== DATASET CONFIGURATION =====")
print("Classes:", data["names"])
print("Number of classes:", data["nc"])1. Lower the confidence threshold
Your model may be missing defects because its confidence threshold is too high.

Find the prediction code in your FastAPI backend. Look for something like:
results = model.predict(    source=image,    conf=0.25,    imgsz=416)



Change it to:
results = model.predict(    source=image,    conf=0.10,    iou=0.50,    imgsz=416,    max_det=100,    save=False)



This allows lower-confidence detections to appear. It may improve recall, but it can also introduce false positives. It does not improve the model's trained weights or actual mAP.
2. Make sure segmentation results are displayed
If you are using YOLO segmentation, use:
annotated_image = results[0].plot()



This draws the predicted bounding boxes, class names and segmentation masks.

Make sure your frontend displays this returned image rather than just showing the uploaded original.
3. Test with three different images
- One image containing a stain.
- One image containing a hole.
- One image containing a needle mark or missing yarn.
Check whether the application returns predictions without crashing. Don't claim successful detection for defects the model misses.

root = yaml_path.parent

for split in ["train", "val", "test"]:
    image_dir = root / data[split].replace("../", "")
    label_dir = image_dir.parent.parent / "labels" / split

    print(f"\n===== {split.upper()} =====")
    print("Image directory:", image_dir)
    print("Label directory:", label_dir)

    if not image_dir.exists() or not label_dir.exists():
        print("Directory not found. Check dataset paths.")
        continue

    images = [
        p for p in image_dir.iterdir()
        if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]
    ]

    labels = list(label_dir.glob("*.txt"))
    counts = Counter()

    for label in labels:
        for line in label.read_text().splitlines():
            values = line.split()

            if values:
                try:
                    class_id = int(float(values[0]))
                    counts[class_id] += 1
                except ValueError:
                    print("Invalid annotation:", label.name)

    print("Images:", len(images))
    print("Label files:", len(labels))
    print("Class distribution:")

    for class_id, name in enumerate(data["names"]):
        print(f"{name}: {counts[class_id]}")

print("\nDataset inspection completed.")
