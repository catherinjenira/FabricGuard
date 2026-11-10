
from ultralytics import YOLO

model = YOLO(
    r"runs/segment/fabricguard_10_epochs/weights/best.pt"
)

metrics = model.val(
    data=r"Febric Defect Detection and Segm.yolov/data.yaml",
    imgsz=640,
    batch=2,
    device="cpu",
    conf=0.001,
    iou=0.6,
    plots=True,
    project="runs/segment",
    name="baseline_evaluation"
)

print("\n========== BASELINE RESULTS ==========")
print("Box mAP50:", metrics.box.map50)
print("Box mAP50-95:", metrics.box.map)
print("Mask mAP50:", metrics.seg.map50)
print("Mask mAP50-95:", metrics.seg.map)
print("\nEvaluation completed!")
