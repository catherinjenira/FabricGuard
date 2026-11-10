"""
FabricGuard-AI Annotation Converter.
Converts Pascal VOC (XML) or COCO (JSON) annotations to YOLO bounding box format.
"""

import os
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

# Standard class mapping
CLASS_MAP = {
    "hole": 0,
    "stain": 1,
    "oil_spot": 1,
    "weaving_slub": 2,
    "slub": 2,
    "yarn_defect": 3,
    "broken_yarn": 3,
    "crease": 4,
    "wrinkle": 4,
    "color_spot": 5,
    "knot": 6,
    "foreign_fiber": 7,
    "foreign_matter": 7
}

def parse_args():
    parser = argparse.ArgumentParser(description="Convert Pascal VOC or COCO annotations to YOLO format.")
    parser.add_argument("--format", type=str, choices=["voc", "coco"], required=True, help="Input annotation format")
    parser.add_argument("--input", type=str, required=True, help="Path to input XML file/directory or COCO JSON file")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save converted .txt labels")
    return parser.parse_args()

def convert_voc_xml(xml_file: Path, output_dir: Path):
    """Converts a single Pascal VOC XML annotation to YOLO format."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    size = root.find("size")
    if size is None:
        print(f"[!] Warning: Missing <size> tag in {xml_file.name}")
        return
        
    width = float(size.find("width").text)
    height = float(size.find("height").text)
    
    if width <= 0 or height <= 0:
        return
        
    yolo_lines = []
    for member in root.findall("object"):
        class_name = member.find("name").text.strip().lower()
        if class_name not in CLASS_MAP:
            continue
            
        class_id = CLASS_MAP[class_name]
        bndbox = member.find("bndbox")
        xmin = float(bndbox.find("xmin").text)
        ymin = float(bndbox.find("ymin").text)
        xmax = float(bndbox.find("xmax").text)
        ymax = float(bndbox.find("ymax").text)
        
        # Calculate normalized center coordinates and dimensions
        x_center = ((xmin + xmax) / 2.0) / width
        y_center = ((ymin + ymax) / 2.0) / height
        box_width = (xmax - xmin) / width
        box_height = (ymax - ymin) / height
        
        # Clamp to [0, 1]
        x_center = max(0.0, min(1.0, x_center))
        y_center = max(0.0, min(1.0, y_center))
        box_width = max(0.0, min(1.0, box_width))
        box_height = max(0.0, min(1.0, box_height))
        
        yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}")
        
    out_file = output_dir / f"{xml_file.stem}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines) + ("\n" if yolo_lines else ""))

def convert_coco_json(coco_path: Path, output_dir: Path):
    """Converts COCO format JSON annotations to YOLO format .txt files."""
    with open(coco_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    image_dict = {img["id"]: img for img in data.get("images", [])}
    category_dict = {cat["id"]: cat["name"].strip().lower() for cat in data.get("categories", [])}
    
    annotations_by_image = {}
    for ann in data.get("annotations", []):
        img_id = ann["image_id"]
        annotations_by_image.setdefault(img_id, []).append(ann)
        
    converted_count = 0
    for img_id, img_info in image_dict.items():
        img_name = Path(img_info["file_name"]).stem
        img_w = float(img_info["width"])
        img_h = float(img_info["height"])
        
        yolo_lines = []
        for ann in annotations_by_image.get(img_id, []):
            cat_name = category_dict.get(ann["category_id"], "")
            if cat_name not in CLASS_MAP:
                continue
                
            class_id = CLASS_MAP[cat_name]
            # COCO bbox: [xmin, ymin, width, height]
            x, y, w, h = ann["bbox"]
            x_center = (x + w / 2.0) / img_w
            y_center = (y + h / 2.0) / img_h
            norm_w = w / img_w
            norm_h = h / img_h
            
            yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")
            
        out_file = output_dir / f"{img_name}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(yolo_lines) + ("\n" if yolo_lines else ""))
        converted_count += 1
        
    print(f"[✓] Converted {converted_count} COCO image annotations to {output_dir}")

def main():
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.format == "voc":
        if input_path.is_file():
            convert_voc_xml(input_path, output_dir)
            print(f"[✓] Converted {input_path.name}")
        elif input_path.is_dir():
            xmls = list(input_path.glob("*.xml"))
            for xml in xmls:
                convert_voc_xml(xml, output_dir)
            print(f"[✓] Converted {len(xmls)} VOC XML files to {output_dir}")
    elif args.format == "coco":
        convert_coco_json(input_path, output_dir)

if __name__ == "__main__":
    main()

