"""
Image preprocessing service for fabric texture enhancement and analysis.
"""

from pathlib import Path
from PIL import Image
import numpy as np

def apply_clahe(image: Image.Image) -> Image.Image:
    """
    Applies Contrast-Limited Adaptive Histogram Equalization (CLAHE)
    to enhance yarn and weave micro-contrasts under varying industrial illumination.
    """
    try:
        import cv2
        np_img = np.array(image.convert("RGB"))
        lab = cv2.cvtColor(np_img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        
        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
        return Image.fromarray(enhanced)
    except Exception:
        # Fallback if cv2 is not present or fails
        return image

def preprocess_image_for_model(image: Image.Image, target_size: int = 640) -> Image.Image:
    """
    Resizes image with letterbox padding to preserve textile yarn aspect ratio.
    """
    w, h = image.size
    scale = min(target_size / w, target_size / h)
    nw, nh = int(w * scale), int(h * scale)
    
    resized = image.resize((nw, nh), Image.Resampling.BILINEAR)
    new_image = Image.new("RGB", (target_size, target_size), (128, 128, 128))
    new_image.paste(resized, ((target_size - nw) // 2, (target_size - nh) // 2))
    return new_image

def save_processed_image(image: Image.Image, output_path: Path) -> str:
    """Saves image to disk and returns string path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, quality=92)
    return str(output_path)

