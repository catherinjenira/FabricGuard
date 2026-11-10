# 📚 FabricGuard-AI Dataset Documentation

This document defines the textile defect taxonomy, YOLO annotation formats, augmentation strategies, and dataset preparation pipelines.

---

## 1. Defect Taxonomy & Class ID Mapping

FabricGuard-AI recognizes 8 distinct surface and structural anomalies encountered in woven and knit manufacturing:

| Class ID | Name | Physical Manifestation | Root Cause in Mill |
|:---:|:---|:---|:---|
| `0` | **Hole** | Physical perforation through warp/weft structure | Broken loom needle, mechanical hook catch |
| `1` | **Stain** | Dark/discolored patch on textile face | Loom lubricating oil, chemical splashing |
| `2` | **Weaving Slub** | Abrupt thick localized segment in yarn | Irregular yarn spinning or uneven roving draft |
| `3` | **Yarn Defect** | Broken filament, missing pick, or loose end | Warp tension failure, bobbin breakage |
| `4` | **Crease** | Sharp permanent wrinkle running warp-wise | Thermal setting misalignment or calender pressure |
| `5` | **Color Spot** | Microscopic drop of foreign dye pigment | Dye kitchen contamination, splatters |
| `6` | **Knot** | Coarse physical knot protruding from surface | Yarn splicing knot passing through reed |
| `7` | **Foreign Fiber** | Discolored lint, hair, or synthetic stray fiber | Ambient fly contamination in weaving shed |

---

## 2. YOLO Bounding Box Annotation Format

Annotations are stored in standard normalized YOLO `.txt` files corresponding to each image:

```
<class_id> <x_center> <y_center> <width> <height>
```

- Coordinate values are normalized to the range `[0.0, 1.0]` relative to image width and height.
- For example, an oil stain centered at $(x=320, y=240)$ in a $640 \times 640$ image with dimensions $64 \times 48$:
  ```
  1 0.500000 0.375000 0.100000 0.075000
  ```

---

## 3. Dataset Directory Structure

```
ml/dataset/
├── data.yaml
├── raw/                      # Unsplit raw factory images & VOC/COCO labels
└── processed/
    ├── images/
    │   ├── train/            # 70% of dataset
    │   ├── val/              # 15% of dataset
    │   └── test/             # 15% of dataset
    └── labels/
        ├── train/
        ├── val/
        └── test/
```

---

## 4. Augmentation Pipeline

To guarantee robust generalization across variable mill lighting and yarn count variations, the training script applies:
1. **Geometric**: Random Horizontal/Vertical Flip ($p=0.5$), Random Rotation ($\pm 15^\circ$).
2. **Photometric**: Contrast jitter ($\pm 20\%$), HSV Saturation jitter ($\pm 15\%$), Gaussian blur ($k=3$).
3. **Mosaic & Mixup**: 4-way mosaic synthesis to detect multi-defect clustered defects.

