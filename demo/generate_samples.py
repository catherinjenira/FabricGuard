"""
Synthetic Fabric Image Generator for FabricGuard-AI Demo.
Generates realistic woven fabric textures with synthetic defect artifacts.
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

def create_base_fabric_pattern(width=640, height=640, base_color=(220, 215, 205)):
    """Generates a textured plain-weave fabric pattern."""
    img = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Simulate warp and weft weave lines
    yarn_step = 6
    for x in range(0, width, yarn_step):
        variance = random.randint(-12, 12)
        c = tuple(max(0, min(255, val + variance)) for val in base_color)
        draw.line([(x, 0), (x, height)], fill=c, width=2)
        
    for y in range(0, height, yarn_step):
        variance = random.randint(-15, 15)
        c = tuple(max(0, min(255, val + variance)) for val in base_color)
        draw.line([(0, y), (width, y)], fill=c, width=2)
        
    # Apply soft blur for natural textile texture
    img = img.filter(ImageFilter.GaussianBlur(radius=0.7))
    return img

def add_hole_defect(img, x=300, y=320, radius=25):
    """Simulates a dark hole/puncture with frayed edges."""
    draw = ImageDraw.Draw(img)
    # Dark center
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(30, 28, 26))
    # Frayed fibers
    for _ in range(40):
        angle = random.uniform(0, 2 * math.pi)
        dist = radius + random.uniform(1, 12)
        fx = x + dist * math.cos(angle)
        fy = y + dist * math.sin(angle)
        draw.line([(x + radius * 0.7 * math.cos(angle), y + radius * 0.7 * math.sin(angle)), (fx, fy)],
                  fill=(160, 150, 140), width=1)
    return img

def add_stain_defect(img, x=220, y=240, r_x=45, r_y=30):
    """Simulates an oil/grease stain with semi-translucent feathered overlay."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(overlay)
    o_draw.ellipse([x - r_x, y - r_y, x + r_x, y + r_y], fill=(90, 70, 40, 160))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=12))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
    return img

def add_slub_defect(img, start_x=120, y=400, length=220, thickness=9):
    """Simulates a thick yarn slub anomaly along the weft."""
    draw = ImageDraw.Draw(img)
    draw.line([(start_x, y), (start_x + length, y)], fill=(120, 115, 105), width=thickness)
    return img

def main():
    target_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(target_dir, exist_ok=True)
    
    print("[*] Generating synthetic fabric samples...")
    # 1. Clean
    clean = create_base_fabric_pattern()
    clean.save(os.path.join(target_dir, "fabric_clean.jpg"), quality=95)
    
    # 2. Hole defect
    hole = create_base_fabric_pattern()
    hole = add_hole_defect(hole, 320, 310, 28)
    hole.save(os.path.join(target_dir, "fabric_hole.jpg"), quality=95)
    
    # 3. Oil stain
    stain = create_base_fabric_pattern()
    stain = add_stain_defect(stain, 280, 260, 50, 35)
    stain.save(os.path.join(target_dir, "fabric_oil_stain.jpg"), quality=95)
    
    # 4. Weaving Slub
    slub = create_base_fabric_pattern()
    slub = add_slub_defect(slub, 160, 380, 240, 8)
    slub.save(os.path.join(target_dir, "fabric_weaving_slub.jpg"), quality=95)
    
    print(f"[✓] Created 4 sample fabric images in {target_dir}")

if __name__ == "__main__":
    main()

