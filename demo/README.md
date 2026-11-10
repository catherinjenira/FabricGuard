# 🧪 FabricGuard-AI Demo & Test Assets

This folder contains testing resources and synthetic fabric sample generators for testing FabricGuard-AI without needing proprietary mill camera feeds.

## Generate Synthetic Test Samples
Run the included python script to generate high-resolution synthetic textile weaves with simulated defects:

```bash
python generate_samples.py
```

This will generate:
- `fabric_clean.jpg` - Defect-free woven cotton/linen texture.
- `fabric_oil_stain.jpg` - Fabric with simulated lubricant oil seepage.
- `fabric_hole.jpg` - Fabric with simulated loom needle puncture/hole.
- `fabric_weaving_slub.jpg` - Fabric with warp yarn thickness anomaly.

