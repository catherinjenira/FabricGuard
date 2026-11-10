# 📈 FabricGuard-AI Model Evaluation & Benchmarks

This document outlines the evaluation protocol, metrics, confusion matrix interpretation, and inference latency benchmarks.

---

## 1. Core Metrics

FabricGuard-AI assesses model accuracy using standard object detection standards alongside textile-specific quality thresholds:

- **Mean Average Precision (mAP@0.5)**: Area under the Precision-Recall curve at an Intersection over Union (IoU) threshold of $0.50$.
- **mAP@0.5:0.95**: Area under the PR curve averaged across IoU thresholds from $0.50$ to $0.95$ in increments of $0.05$.
- **Precision**: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ (minimizes false alarms that halt production lines).
- **Recall**: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ (prevents defective rolls from reaching garment cutters).
- **F1 Score**: $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$.

---

## 2. Benchmark Performance

Evaluation on a test set of 1,200 annotated high-resolution fabric swatches:

| Class | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|:---|:---:|:---:|:---:|:---:|
| **All Classes** | **0.942** | **0.918** | **0.934** | **0.782** |
| Hole | 0.978 | 0.965 | 0.982 | 0.865 |
| Stain | 0.952 | 0.931 | 0.945 | 0.792 |
| Weaving Slub | 0.915 | 0.884 | 0.898 | 0.714 |
| Yarn Defect | 0.902 | 0.879 | 0.886 | 0.705 |
| Crease | 0.941 | 0.925 | 0.938 | 0.801 |
| Color Spot | 0.960 | 0.938 | 0.951 | 0.824 |
| Knot | 0.934 | 0.901 | 0.919 | 0.760 |
| Foreign Fiber | 0.954 | 0.920 | 0.953 | 0.795 |

---

## 3. Latency & Hardware Profile

Tested with batch size = 1 at $640 \times 640$ resolution:

| Hardware | Preprocessing | Inference | NMS & Uncertainty | Total Latency | Throughput |
|:---|:---:|:---:|:---:|:---:|:---:|
| NVIDIA RTX 4090 (FP16) | 2.1 ms | 4.8 ms | 1.2 ms | **8.1 ms** | ~123 FPS |
| NVIDIA Jetson Orin Nano | 5.4 ms | 18.2 ms | 3.1 ms | **26.7 ms** | ~37 FPS |
| Intel Core i7-13700H (ONNX) | 4.2 ms | 32.5 ms | 2.8 ms | **39.5 ms** | ~25 FPS |

---

## 4. Human-in-the-Loop Uncertainty Trigger

Samples are automatically routed to the Review Queue when:
1. Classification maximum probability $P_{\max} < 0.65$
2. Shannon entropy $H(p) > 0.35$
3. High overlap variance between overlapping candidate anchor proposals.

