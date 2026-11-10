# 🧵 FabricGuard-AI: Automated Industrial Fabric Defect Inspection System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](backend/)
[![React + Vite](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?logo=react)](frontend/)
[![YOLO Computer Vision](https://img.shields.io/badge/AI%20Model-YOLO%20%2F%20Deep%20Learning-FF6F00.svg)](ml/)

**FabricGuard-AI** is a production-grade, human-in-the-loop (HITL) computer vision platform designed for real-time fabric defect detection, classification, and quality assurance in textile manufacturing lines.

---

## 🌟 Key Features

- **⚡ Real-Time Inspection**: High-throughput defect detection using deep learning (YOLOv8/v11 architecture) with millisecond-level inference.
- **🎯 8 Defect Classes**: Detects holes, oil stains, weaving slubs, yarn breaks, creases, color spots, knots, and foreign fibers.
- **🔍 Active Uncertainty Estimation**: Quantifies prediction uncertainty (entropy and boundary confidence) to automatically route borderline samples to a Human-in-the-Loop review queue.
- **🧑‍🏭 Human-in-the-Loop (HITL) Review Panel**: Allows QA inspectors to approve, reject, re-classify, or re-draw defect bounding boxes.
- **📦 Batch Inspection & Bulk Processing**: Process entire rolls or multi-image batches with automated pass/fail aggregation and exportable reports.
- **📊 Quality Analytics & Model Drift Telemetry**: Track precision, recall, mAP@0.5, false positive trends, and defect distribution over time.
- **🛡️ Industrial-Grade Modern UI**: Dark-themed, responsive dashboard built with React 18, Vite, and Tailwind CSS.

---

## 📁 Repository Structure

```tree
FabricGuard-AI/
├── frontend/                     # React + Vite Web Application
│   ├── public/                   # Static assets & favicon
│   ├── src/
│   │   ├── assets/               # Icons & logos
│   │   ├── components/           # Reusable UI widgets
│   │   │   ├── Sidebar.jsx       # Navigation drawer
│   │   │   ├── Navbar.jsx        # Top control bar
│   │   │   ├── StatCard.jsx      # Metric stat cards
│   │   │   ├── ImageUploader.jsx # Drag-and-drop fabric uploader
│   │   │   ├── DetectionResult.jsx   # Defect diagnosis breakdown
│   │   │   ├── BoundingBoxViewer.jsx # Interactive canvas & bounding overlay
│   │   │   ├── ConfidenceBadge.jsx   # Defect confidence badge
│   │   │   ├── ReviewPanel.jsx       # HITL review action panel
│   │   │   └── BatchTable.jsx        # Batch roll data grid
│   │   ├── pages/                # Main application views
│   │   │   ├── Dashboard.jsx         # Executive overview
│   │   │   ├── Inspection.jsx        # Single-image real-time inspection
│   │   │   ├── BatchInspection.jsx   # High-volume roll inspection
│   │   │   ├── ReviewQueue.jsx       # Flagged uncertainty triage
│   │   │   ├── History.jsx           # Audit logs & search
│   │   │   └── ModelPerformance.jsx  # Accuracy, mAP & confusion matrix
│   │   ├── services/             # Axios API client & services
│   │   ├── hooks/                # React custom hooks (useInspection)
│   │   ├── utils/                # Formatters & input validation
│   │   ├── App.jsx               # Application routes
│   │   ├── main.jsx              # React DOM entry
│   │   └── index.css             # Tailwind CSS tokens & styling
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
├── backend/                      # FastAPI Python Service
│   ├── app/
│   │   ├── main.py               # FastAPI application entry & middleware
│   │   ├── api/routes/           # REST endpoints
│   │   │   ├── inspection.py     # Single image inference endpoint
│   │   │   ├── batch.py          # Batch inspection queue
│   │   │   ├── history.py        # Inspection audit trails
│   │   │   ├── review.py         # HITL decision submissions
│   │   │   └── evaluation.py     # Model metrics & drift stats
│   │   ├── core/                 # Config & Database sessions
│   │   │   ├── config.py         # Settings & environment parser
│   │   │   └── database.py       # SQLAlchemy SQLite/PostgreSQL engine
│   │   ├── services/             # Business & AI logic
│   │   │   ├── inference.py      # YOLO loader & fallback detector
│   │   │   ├── image_processing.py # CLAHE, normalization, annotation
│   │   │   ├── uncertainty.py    # Shannon entropy & confidence scorer
│   │   │   ├── review_service.py # Audit logger & active learning recorder
│   │   │   └── evaluation_service.py # Telemetry calculations
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic v2 schemas
│   │   └── utils/                # File & image helpers
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── ml/                           # Machine Learning Pipeline
│   ├── dataset/                  # Dataset directory
│   │   ├── raw/                  # Raw unprocessed fabric images
│   │   ├── processed/            # Train / Val / Test YOLO splits
│   │   └── data.yaml             # YOLO dataset configuration
│   ├── scripts/
│   │   ├── prepare_dataset.py    # Dataset acquisition & train-test split
│   │   ├── convert_annotations.py# Conversion from VOC/COCO to YOLO txt
│   │   ├── train.py              # YOLO training with PyTorch
│   │   ├── evaluate.py           # Evaluation & metric calculation
│   │   └── predict.py            # Standalone CLI inference
│   ├── weights/                  # Model checkpoints (best.pt, last.pt)
│   └── results/                  # Confusion matrix & metrics.json
│
├── docs/                         # Engineering Documentation
│   ├── architecture.md           # System architecture & HITL design
│   ├── dataset_documentation.md  # Defect catalog & annotation specs
│   ├── model_evaluation.md       # Benchmarks & uncertainty formulas
│   └── screenshots/              # UI walkthrough screenshots
├── demo/                         # Demo samples & test assets
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js** >= 18.x
- **Python** >= 3.10
- *(Optional)* CUDA-compatible GPU for accelerated model training

### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend API docs will be live at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 Machine Learning Pipeline

Train your custom YOLO fabric defect detection model:

```bash
cd ml

# 1. Prepare and split dataset
python scripts/prepare_dataset.py --source dataset/raw --split 0.7 0.15 0.15

# 2. Train YOLO model
python scripts/train.py --epochs 50 --imgsz 640 --batch 16

# 3. Evaluate on test set
python scripts/evaluate.py --weights weights/best.pt

# 4. Predict on a test sample
python scripts/predict.py --source ../demo/sample_defect.jpg --conf 0.45
```

---

## 📊 Defect Classification Taxonomy

| Class ID | Defect Name | Description | Severity |
|----------|-------------|-------------|----------|
| `0` | Hole | Punctures or physical tears in weave | Critical |
| `1` | Stain | Oil, chemical, or dye discoloration | High |
| `2` | Weaving Slub | Thickness anomaly in warp/weft yarn | Medium |
| `3` | Yarn Defect | Broken filament or loose thread | Medium |
| `4` | Crease | Pressing defect or mechanical fold | Low |
| `5` | Color Spot | Bleed or foreign dye contamination | Medium |
| `6` | Knot | Yarn splicing knot protruding | Low |
| `7` | Foreign Fiber | Lint, hair, or synthetic contamination | Medium |

---

## 🔒 Security & Quality Assurance
- Automated file-signature MIME validation prevents malicious uploads.
- Full audit log traceability for all human-reviewer actions and overrides.
- Model uncertainty filtering prevents unverified automated pass decisions.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

