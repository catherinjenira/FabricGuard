"""
FabricGuard-AI Dataset Preparation Script.
Splits raw paired images and annotations into train, val, and test splits for YOLO training.
"""

import os
import shutil
import random
import argparse
from pathlib import Path

VALID_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def parse_args():
    parser = argparse.ArgumentParser(description="Prepare and split fabric defect dataset for YOLO.")
    parser.add_argument("--source", type=str, default="dataset/raw", help="Path to raw dataset directory")
    parser.add_argument("--output", type=str, default="dataset/processed", help="Path to output processed dataset directory")
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Train split ratio (default: 0.70)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Val split ratio (default: 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test split ratio (default: 0.15)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    return parser.parse_args()

def collect_image_label_pairs(source_dir: Path):
    """Finds all matching image and label file pairs."""
    pairs = []
    for file_path in source_dir.rglob("*"):
        if file_path.suffix.lower() in VALID_IMAGE_EXTS:
            label_path = file_path.with_suffix(".txt")
            if label_path.exists():
                pairs.append((file_path, label_path))
            else:
                # Defect-free background image with no annotations
                pairs.append((file_path, None))
    return pairs

def prepare_splits(pairs, train_ratio, val_ratio, test_ratio, seed=42):
    """Shuffles and partitions file pairs into train, val, and test splits."""
    random.seed(seed)
    shuffled = pairs.copy()
    random.shuffle(shuffled)
    
    total = len(shuffled)
    if total == 0:
        return [], [], []
        
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    
    train_set = shuffled[:train_end]
    val_set = shuffled[train_end:val_end]
    test_set = shuffled[val_end:]
    
    return train_set, val_set, test_set

def copy_split_files(split_items, split_name, output_dir: Path):
    """Copies images and labels to their destination split directories."""
    img_dest = output_dir / "images" / split_name
    lbl_dest = output_dir / "labels" / split_name
    
    img_dest.mkdir(parents=True, exist_ok=True)
    lbl_dest.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    for img_path, lbl_path in split_items:
        dest_img = img_dest / img_path.name
        shutil.copy2(img_path, dest_img)
        
        if lbl_path and lbl_path.exists():
            dest_lbl = lbl_dest / lbl_path.name
            shutil.copy2(lbl_path, dest_lbl)
        else:
            # Create empty label file for negative/background samples
            empty_lbl = lbl_dest / (img_path.stem + ".txt")
            empty_lbl.touch(exist_ok=True)
        copied += 1
        
    return copied

def main():
    args = parse_args()
    source_dir = Path(args.source)
    output_dir = Path(args.output)
    
    print(f"[*] Scanning source directory: {source_dir}")
    pairs = collect_image_label_pairs(source_dir)
    print(f"[*] Total image samples found: {len(pairs)}")
    
    if not pairs:
        print(f"[!] Warning: No images found in {source_dir}. Place raw images and .txt labels in dataset/raw.")
        return
        
    train_set, val_set, test_set = prepare_splits(
        pairs, args.train_ratio, args.val_ratio, args.test_ratio, args.seed
    )
    
    print(f"[*] Splitting dataset into: Train={len(train_set)}, Val={len(val_set)}, Test={len(test_set)}")
    
    copy_split_files(train_set, "train", output_dir)
    copy_split_files(val_set, "val", output_dir)
    copy_split_files(test_set, "test", output_dir)
    
    print(f"[✓] Dataset prepared successfully in: {output_dir}")

if __name__ == "__main__":
    main()

