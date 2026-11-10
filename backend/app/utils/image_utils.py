"""
Image processing and coordinate conversion helpers.
"""

import io
import base64
from typing import Tuple, List, Dict, Any
from PIL import Image, ImageDraw, ImageFont

DEFECT_PALETTE = {
    0: (239, 68, 68),    # Hole: Red
    1: (245, 158, 11),   # Stain: Amber
    2: (168, 85, 247),   # Weaving Slub: Purple
    3: (59, 130, 246),   # Yarn Defect: Blue
    4: (16, 185, 129),   # Crease: Emerald
    5: (236, 72, 153),   # Color Spot: Pink
    6: (20, 184, 166),   # Knot: Teal
    7: (249, 115, 22),   # Foreign Fiber: Orange
}

CLASS_NAME_MAP = {
    0: "hole",
    1: "stain",
    2: "weaving_slub",
    3: "yarn_defect",
    4: "crease",
    5: "color_spot",
    6: "knot",
    7: "foreign_fiber"
}

def to_base64_thumbnail(img: Image.Image, max_dim: int = 180) -> str:
    """Generates a small base64 JPEG thumbnail."""
    thumb = img.copy()
    thumb.thumbnail((max_dim, max_dim))
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=80)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

def normalized_to_pixels(box: Dict[str, float], img_w: int, img_h: int) -> Tuple[int, int, int, int]:
    """Converts normalized bbox dict {xmin, ymin, xmax, ymax} to pixel box (x1, y1, x2, y2)."""
    x1 = int(box["xmin"] * img_w)
    y1 = int(box["ymin"] * img_h)
    x2 = int(box["xmax"] * img_w)
    y2 = int(box["ymax"] * img_h)
    return max(0, x1), max(0, y1), min(img_w, x2), min(img_h, y2)

def draw_defect_boxes(img: Image.Image, detections: List[Dict[str, Any]]) -> Image.Image:
    """Draws color-coded bounding boxes and labels onto an image copy."""
    annotated = img.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    for det in detections:
        cls_id = det.get("class_id", 0)
        conf = det.get("confidence", 0.0)
        name = det.get("class_name", CLASS_NAME_MAP.get(cls_id, "defect"))
        box = det.get("box")

        if isinstance(box, dict):
            x1, y1, x2, y2 = normalized_to_pixels(box, w, h)
        else:
            x1, y1, x2, y2 = box

        color = DEFECT_PALETTE.get(cls_id, (255, 0, 0))
        
        # Bounding outline
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        
        # Label tag
        label = f"{name} {conf:.0%}"
        text_w = len(label) * 8
        draw.rectangle([x1, max(0, y1 - 20), x1 + text_w + 8, y1], fill=color)
        draw.text((x1 + 4, max(0, y1 - 18)), label, fill=(255, 255, 255))

    return annotated

