"""
FabricGuard-AI: High-Accuracy YOLO11-seg Training & Fine-Tuning Pipeline
Specifically optimized for fine-grained fabric defects (Needle Marks, Holes, Missing Yarns, Stains).
"""

import os
import argparse
import shutil
from pathlib import Path
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="Train high-accuracy fabric defect segmentation model.")
    parser.add_argument("--data", type=str, default="Febric Defect Detection and Segm.yolov/data.yaml", help="Path to data.yaml")
    parser.add_argument("--weights", type=str, default="runs/segment/fabricguard_10_epochs/weights/best.pt", help="Pretrained checkpoint to fine-tune from")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=4, help="Batch size (use 8 or 16 if GPU memory permits)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution (640 for sharp micro-fiber defects)")
    parser.add_argument("--device", type=str, default="cpu", help="Device: '0' for CUDA GPU, 'cpu' for CPU")
    parser.add_argument("--project", type=str, default="runs/segment", help="Project save directory")
    parser.add_argument("--name", type=str, default="fabricguard_high_accuracy", help="Experiment name")
    return parser.parse_args()

def main():
    args = parse_args()

    print("=" * 70)
    print("🧵 FabricGuard-AI: High-Accuracy Model Training Pipeline")
    print(f"Data:       {args.data}")
    print(f"Base:       {args.weights}")
    print(f"Epochs:     {args.epochs} | Batch: {args.batch} | ImgSz: {args.imgsz}")
    print(f"Device:     {args.device}")
    print("=" * 70)

    # Load model (fine-tune from existing learned checkpoint)
    if Path(args.weights).exists():
        print(f"[✓] Loading existing checkpoint for warm-start: {args.weights}")
        model = YOLO(args.weights)
    else:
        print("[*] Base checkpoint not found, starting from yolo11n-seg.pt")
        model = YOLO("yolo11n-seg.pt")

    # High-Accuracy Hyperparameters Tuned for Textile Inspection
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        
        # Optimizer & Learning Rate Schedule
        optimizer="AdamW",       # AdamW converges significantly better on small/medium textile datasets
        lr0=0.002,               # Initial learning rate
        lrf=0.01,                # Final learning rate fraction (0.002 * 0.01 = 2e-5)
        cos_lr=True,             # Cosine annealing schedule prevents getting stuck in local minima
        warmup_epochs=3,         # Warm-up stabilizes gradients
        warmup_momentum=0.8,
        
        # Textile-Specific Augmentation Strategy
        fliplr=0.5,              # Horizontal flip (fabrics are symmetrical)
        flipud=0.5,              # Vertical flip
        degrees=10.0,            # Small rotation accounting for yarn orientation variance
        scale=0.5,               # Multi-scale zooming
        translate=0.1,           # Small translations
        mosaic=0.8,              # Mosaic helps learn multi-defect swatches
        close_mosaic=5,          # Disables mosaic in last 5 epochs for razor-sharp edge boundaries
        mixup=0.15,              # Mixup regularization prevents overfitting on background textures
        
        # Loss Gains Tuned for Segmentation
        box=7.5,                 # Bounding box loss gain
        cls=0.5,                 # Classification loss gain
        dfl=1.5,                 # Distribution focal loss gain
        
        # Validation & Checkpointing
        save=True,
        save_period=5,
        plots=True,
        patience=10              # Early stopping if no improvement for 10 epochs
    )

    print("\n[✓] Training complete! Evaluating on validation set...")
    val_metrics = model.val(data=args.data, imgsz=args.imgsz, device=args.device)

    print(f"[✓] Final Box mAP50:  {val_metrics.box.map50:.4f}")
    print(f"[✓] Final Mask mAP50: {val_metrics.seg.map50:.4f}")

    # Copy best weights to ml/weights/best.pt for backend integration
    best_weights = Path(args.project) / args.name / "weights" / "best.pt"
    if best_weights.exists():
        target = Path("ml/weights/best.pt")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, target)
        print(f"[✓] Updated backend model weights: {target.resolve()}")

if __name__ == "__main__":
    main()
