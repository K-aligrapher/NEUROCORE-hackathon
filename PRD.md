# 🩸 HemaVision — Blood Smear Analysis & Disease Detection System
## Product Requirements Document (PRD)

**Version:** 1.0.0  
**Date:** May 2026  
**Status:** Active Development  
**Document Type:** Full-Stack Product Requirements  
**Classification:** Hackathon Build — Biomedical AI Track  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision & Mission](#2-product-vision--mission)
3. [Target Users & Personas](#3-target-users--personas)
4. [Problem Statement & Market Context](#4-problem-statement--market-context)
5. [Disease Scope & Clinical Rationale](#5-disease-scope--clinical-rationale)
6. [System Architecture Overview](#6-system-architecture-overview)
7. [AI Pipeline Design](#7-ai-pipeline-design)
   - 7.1 Stage 1: Blood Cell Segmentation Module
   - 7.2 Stage 2: Cell Enhancement Pipeline
   - 7.3 Stage 3: Disease Classification Models
   - 7.4 Model Training Strategy
   - 7.5 Inference Pipeline
8. [Backend Architecture](#8-backend-architecture)
   - 8.1 Technology Stack
   - 8.2 API Design (REST + WebSocket)
   - 8.3 Database Schema
   - 8.4 File Storage
   - 8.5 Queue & Job Management
   - 8.6 Authentication & Security
9. [Frontend Architecture](#9-frontend-architecture)
   - 9.1 Tech Stack & Design System
   - 9.2 Page & Screen Specifications
   - 9.3 Component Library
   - 9.4 State Management
   - 9.5 UI/UX Guidelines
10. [Data Engineering & Datasets](#10-data-engineering--datasets)
11. [Model Training Infrastructure](#11-model-training-infrastructure)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Testing Strategy](#13-testing-strategy)
14. [Performance Benchmarks & KPIs](#14-performance-benchmarks--kpis)
15. [Ethical Considerations & Compliance](#15-ethical-considerations--compliance)
16. [Project Roadmap & Milestones](#16-project-roadmap--milestones)
17. [File & Folder Structure](#17-file--folder-structure)
18. [Environment Configuration](#18-environment-configuration)
19. [Third-Party Integrations](#19-third-party-integrations)
20. [Appendix: Prompt Engineering & Model Cards](#20-appendix-prompt-engineering--model-cards)

---

## 1. Executive Summary

**HemaVision** is an end-to-end AI-powered blood smear analysis platform designed to assist healthcare professionals, laboratory technicians, and researchers in the rapid detection of hematological diseases through automated microscopic image analysis.

The system ingests a raw microscopic blood smear image (Giemsa-stained or Wright-stained), performs intelligent cell segmentation to isolate individual blood cells, applies morphological enhancement algorithms, and runs a multi-model classification pipeline to detect and report on three clinically significant diseases: **Malaria**, **Sickle Cell Anemia**, and **Thalassemia / Iron Deficiency Anemia**.

The platform is built to be:
- **Clinically accurate**: targeting ≥ 92% sensitivity and ≥ 90% specificity per disease class
- **Explainable**: heatmaps and annotations overlaid on cells for clinical interpretability
- **Fast**: end-to-end inference under 30 seconds for a standard smear image
- **Accessible**: web-based interface requiring no specialized hardware beyond a digital microscope or camera

This document serves as the complete technical and product blueprint for building HemaVision from scratch — covering AI model architecture, backend systems, database design, API contracts, frontend UI, deployment, and testing.

---

## 2. Product Vision & Mission

### Vision Statement

> "Democratize hematological diagnostics — making expert-level blood disease detection accessible to any clinic, anywhere in the world, with nothing more than a microscope image and a browser."

### Mission

To build a robust, explainable AI system that augments (never replaces) medical professionals in detecting life-threatening blood diseases early, accurately, and affordably — particularly targeting resource-constrained healthcare environments in developing nations where specialist access is limited.

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Accuracy First** | Clinical decisions depend on this system. No shortcuts on model precision. |
| **Explainability** | Every prediction must be backed by visual evidence the clinician can verify. |
| **Speed** | Faster than a manual lab technician for routine screening. |
| **Privacy** | All patient data processed with strict anonymization; no images stored without consent. |
| **Modularity** | New diseases and new model versions can be added without rebuilding the stack. |
| **Accessibility** | Runs on mid-range hardware; no GPU required at inference time. |

---

## 3. Target Users & Personas

### Persona 1: Dr. Priya — Rural Healthcare Clinician
- **Background**: MBBS doctor running a primary health center in rural Maharashtra with limited lab infrastructure
- **Pain Point**: Malaria cases often go undiagnosed for 48+ hours waiting for manual smear review
- **Need**: Fast, reliable first-pass screening tool that flags high-risk cases for specialist referral
- **Tech Comfort**: Moderate — comfortable with web apps; no CLI or ML expertise
- **Use Case**: Uploads patient smear photo taken on a $200 USB microscope; gets result in under 30 seconds

### Persona 2: Rajan — Lab Technician
- **Background**: Certified medical lab technician at a district hospital processing 100+ smears per day
- **Pain Point**: Manual counting of parasitized cells is exhausting, error-prone, and slow under high load
- **Need**: Automated cell counting with cell-by-cell breakdown and exportable reports
- **Tech Comfort**: High — uses lab software daily
- **Use Case**: Batch uploads 20 smear images; reviews the flagged anomalies; exports PDF report for records

### Persona 3**: Prof. Anand — Medical Researcher / Educator
- **Background**: Hematology professor using the system for teaching and research dataset curation
- **Pain Point**: Lack of annotated training data and reproducible analysis pipelines
- **Need**: Access to segmented cell crops, model confidence scores, and exportable annotations
- **Tech Comfort**: Expert — can use APIs directly
- **Use Case**: Pulls the REST API programmatically to analyze a batch of research smears and export JSON annotations

### Persona 4: Dev Team / Hackathon Judges
- **Background**: Technical evaluators assessing the completeness, innovation, and clinical relevance of the solution
- **Need**: Well-documented, deployable system with demo capability
- **Use Case**: Clone repo, run `docker-compose up`, visit localhost, upload sample image, see result

---

## 4. Problem Statement & Market Context

### The Problem

Blood-borne diseases — particularly Malaria, Sickle Cell Anemia, and Thalassemia — collectively affect hundreds of millions of people globally:

- **Malaria** causes approximately 600,000 deaths annually (WHO 2023), with 95% occurring in Sub-Saharan Africa. The gold standard diagnosis — manual Giemsa smear microscopy — requires a trained technician and 30–60 minutes per sample.
- **Sickle Cell Anemia** affects ~300,000 newborns annually. In India alone, 40,000 children are born with it each year. Early detection dramatically improves outcomes through prophylactic treatment.
- **Thalassemia** affects ~270 million people worldwide as carriers, with ~56,000 children born annually with the severe form. Diagnosis requires distinguishing subtle morphological changes in red blood cells.

Manual microscopic analysis is:
1. **Slow**: 30–90 minutes per smear
2. **Inconsistent**: Inter-observer variability up to 20%
3. **Inaccessible**: Requires expert technicians unavailable in rural areas
4. **Fatiguing**: Error rates increase sharply after processing 50+ samples

### The Opportunity

Computer vision and deep learning have reached a maturity point where automated cell analysis can match or exceed expert-level performance. HemaVision capitalizes on:

1. **Open datasets**: High-quality labeled datasets (NIH Malaria Cell Images, Chula RBC-12, ALL-IDB) are publicly available
2. **Commodity hardware**: Modern CNNs run inference on CPU in under 30 seconds
3. **Web accessibility**: A browser-based system requires zero client-side installation
4. **Explainable AI**: Grad-CAM and LIME make model decisions interpretable to clinicians

### Competitive Differentiation

| Feature | HemaVision | Traditional Labs | Existing AI Tools |
|---------|-----------|-----------------|-------------------|
| Multi-disease detection | ✅ 3 diseases | ✅ (slow) | ❌ Usually 1 disease |
| Cell-level segmentation + crop | ✅ | ❌ | Partial |
| Explainability (heatmaps) | ✅ | ❌ | Rare |
| Web-based, no install | ✅ | ❌ | Partial |
| Open source | ✅ | ❌ | Mostly paid |
| < 30 sec inference | ✅ | ❌ | Partial |
| Batch processing | ✅ | ✅ | Rare |
| Exportable report (PDF) | ✅ | ✅ | Rare |

---

## 5. Disease Scope & Clinical Rationale

The system is designed to detect exactly three diseases in version 1.0. This choice is deliberate — these three diseases form a clinically complementary and computationally distinct detection set.

---

### 5.1 Malaria

**Clinical Background**:  
Malaria is caused by *Plasmodium* parasites transmitted by *Anopheles* mosquitoes. The primary species of interest are *P. falciparum* (most lethal), *P. vivax*, *P. malariae*, and *P. ovale*.

**Morphological Features for Detection**:
- Ring-form trophozoites visible inside RBCs: small, ring-shaped dark structures approximately 1–2 µm in diameter
- Multiple infections per cell possible in *P. falciparum* (double ring forms)
- Cell may appear normal size or slightly enlarged depending on species
- Maurer's clefts visible in *P. falciparum*-infected cells at later stages
- Schuffner's dots visible in *P. vivax* and *P. ovale* infections

**What the Model Learns**:
- Texture anomalies inside RBC cytoplasm
- Small dark punctate structures within cells
- Binary classification: Parasitized vs. Uninfected per cell
- Confidence calibration for ring-form detection

**Ground Truth Datasets**:
- NIH/NIAID Malaria Cell Images Dataset: 27,558 cell images (13,779 parasitized, 13,779 uninfected)
- Kaggle Malaria Cell Images Dataset (same source, preprocessed)

**Clinical Significance**:  
Sensitivity ≥ 95% is the target because false negatives (missed malaria) are clinically catastrophic.

---

### 5.2 Sickle Cell Anemia

**Clinical Background**:  
Sickle Cell Disease (SCD) is caused by a mutation in the HBB gene producing hemoglobin S. Under low-oxygen conditions, HbS polymerizes and deforms RBCs into characteristic crescent/sickle shapes.

**Morphological Features for Detection**:
- **Sickle cells**: Elongated crescent or banana-shaped RBCs (most distinctive)
- **Target cells**: RBCs with a central dense spot surrounded by a pale ring — also seen in Thalassemia
- **Drepanocytes**: Classic sickle shape
- **Irreversibly sickled cells (ISC)**: Dense, rigid, permanently deformed
- **Normal biconcave disc shape absent** in high-percentage fields during crisis

**What the Model Learns**:
- Cell boundary shape and contour analysis
- Aspect ratio and circularity deviation metrics
- Shape-based classification (shape descriptors + CNN features)
- Multi-class: Normal / Sickle / Target / Other Abnormal

**Ground Truth Datasets**:
- SCD dataset from Erasmus MC (Dutch hospital, annotated)
- Augmented from BCCD Dataset (Blood Cell Count Dataset)
- Synthetic augmentation using AugSim (affine transforms on confirmed sickle cells)

**Clinical Significance**:  
Distinguishing sickle from normal cells is a shape problem — extremely well-suited for CNNs. This is the highest-accuracy model in the pipeline, targeting ≥ 97% AUC.

---

### 5.3 Thalassemia / Iron Deficiency Anemia

**Clinical Background**:  
Thalassemia results from reduced or absent synthesis of hemoglobin chains (alpha or beta). Iron Deficiency Anemia (IDA) results from insufficient iron for hemoglobin production. Both present with hypochromic, microcytic RBCs but with some distinguishing morphological features.

**Morphological Features for Detection**:
- **Hypochromic cells**: Large central pallor area (> 1/3 of cell diameter), washed-out appearance
- **Microcytic cells**: Cells smaller than normal (< 6 µm diameter vs normal 6–8 µm)
- **Target cells (codocytes)**: Bullseye appearance — dense center + pale ring + dense outer rim (more specific to Thalassemia than IDA)
- **Poikilocytosis**: Irregular shapes — elliptocytes, pencil cells (more common in IDA)
- **Basophilic stippling**: Fine purple granules in cytoplasm (Thalassemia trait)
- **Anisocytosis**: Variable cell sizes across the field

**What the Model Learns**:
- Color intensity distribution inside cell (central pallor ratio)
- Cell size normalization relative to surrounding cells
- Multi-feature classification combining color, texture, and shape
- Differentiation: Normal / Hypochromic-Microcytic / Target Cell / Pencil Cell

**Ground Truth Datasets**:
- Chula RBC-12: 12 classes of RBC morphology from Chulalongkorn University (Thailand)
- LISC Dataset (Leukocyte Images for Segmentation and Classification) — supplementary
- Custom augmented IDA images from published clinical microscopy databases

---

### 5.4 Multi-Disease Interaction & Co-occurrence Handling

A single smear may contain cells indicating multiple conditions (e.g., a thalassemia patient contracting malaria). The system handles this by:

1. **Per-cell independent classification**: Each segmented cell gets scored for all three diseases independently
2. **Smear-level aggregation**: Statistics across all cells determine a smear-level report
3. **Conflict flagging**: If >5% of cells flag positive for two diseases simultaneously, a "complex smear — specialist review required" alert is raised
4. **Minimum cell count enforcement**: Results are marked unreliable if fewer than 50 RBCs are detected in the segmentation stage

---

## 6. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HemaVision System                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐    ┌─────────────────────────────────────────┐   │
│   │  Web Client │    │           Backend (FastAPI)              │   │
│   │  (React +   │◄──►│  ┌─────────┐  ┌─────────┐  ┌────────┐ │   │
│   │  Tailwind)  │    │  │Auth/JWT │  │REST API │  │WS API  │ │   │
│   └─────────────┘    │  └─────────┘  └────┬────┘  └───┬────┘ │   │
│                       │                    │           │       │   │
│                       │  ┌─────────────────▼───────────▼────┐ │   │
│                       │  │         Job Queue (Celery)        │ │   │
│                       │  └─────────────────┬────────────────┘ │   │
│                       │                    │                   │   │
│                       │  ┌─────────────────▼────────────────┐ │   │
│                       │  │        AI Inference Engine        │ │   │
│                       │  │  ┌────────────┐ ┌─────────────┐  │ │   │
│                       │  │  │ Segmentor  │ │  Enhancer   │  │ │   │
│                       │  │  │(YOLOv8/   │ │(CLAHE+      │  │ │   │
│                       │  │  │ SAM-Lite) │ │ Normalize)  │  │ │   │
│                       │  │  └─────┬──────┘ └──────┬──────┘  │ │   │
│                       │  │        └────────┬────────┘         │ │   │
│                       │  │  ┌─────────────▼──────────────┐   │ │   │
│                       │  │  │    Disease Classifiers     │   │ │   │
│                       │  │  │  ┌─────┐ ┌──────┐ ┌─────┐ │   │ │   │
│                       │  │  │  │MLR  │ │SCD   │ │THAL │ │   │ │   │
│                       │  │  │  │CNN  │ │CNN   │ │CNN  │ │   │ │   │
│                       │  │  │  └─────┘ └──────┘ └─────┘ │   │ │   │
│                       │  │  └────────────────────────────┘   │ │   │
│                       │  │  ┌─────────────────────────────┐  │ │   │
│                       │  │  │  Grad-CAM / Explainability  │  │ │   │
│                       │  │  └─────────────────────────────┘  │ │   │
│                       │  └──────────────────────────────────┘ │   │
│                       │                                        │   │
│                       │  ┌──────────┐ ┌──────────┐ ┌───────┐ │   │
│                       │  │PostgreSQL│ │  Redis   │ │MinIO  │ │   │
│                       │  │(results) │ │(cache/   │ │(image │ │   │
│                       │  │          │ │ queue)   │ │storage│ │   │
│                       │  └──────────┘ └──────────┘ └───────┘ │   │
│                       └────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Frontend | React 18, Tailwind CSS, shadcn/ui | User interface |
| Backend API | FastAPI (Python 3.11) | REST + WebSocket endpoints |
| Task Queue | Celery + Redis | Async ML job processing |
| Segmentation | YOLOv8n / SAM-Lite | Cell detection & isolation |
| Enhancement | OpenCV (CLAHE, bilateral filter) | Image quality pipeline |
| Classification | EfficientNet-B2 / MobileNetV3 | Disease prediction |
| Explainability | Grad-CAM, LIME | Heatmap generation |
| Database | PostgreSQL 15 | Persistent storage |
| Cache | Redis 7 | Job queue + response cache |
| Object Storage | MinIO (S3-compatible) | Image + result storage |
| ML Experiment Tracking | MLflow | Model versioning |
| Containerization | Docker + Docker Compose | Deployment |
| Reverse Proxy | Nginx | Load balancing, SSL |
| Monitoring | Prometheus + Grafana | Metrics & alerting |

---

## 7. AI Pipeline Design

The AI pipeline is a sequential two-stage architecture:

**Stage 1**: Whole-smear image → Cell segmentation → Individual cell crops  
**Stage 2**: Cell crops → Enhancement → Disease classification → Explainability maps

```
INPUT IMAGE (full smear)
        │
        ▼
┌───────────────────┐
│   Preprocessing   │  Resize, normalize, convert to RGB
│   (global)        │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Cell Detection  │  YOLOv8n (fast) or SAM-Lite (accurate)
│   & Segmentation  │  → bounding boxes + masks for each RBC
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Cell Cropping    │  Crop each detected cell with 5px padding
│  & Validation     │  Filter: min size 15px, max size 150px
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Cell Enhancement │  CLAHE (contrast), bilateral filter (noise),
│  Pipeline         │  stain normalization (Macenko method),
│                   │  background masking (circular crop)
└────────┬──────────┘
         │
         ├──────────────────┬─────────────────┐
         ▼                  ▼                 ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────────┐
│ Malaria CNN    │ │ Sickle Cell    │ │ Thalassemia CNN  │
│ (EfficientNet  │ │ CNN            │ │ (EfficientNet-B2 │
│  -B0)          │ │ (MobileNetV3 + │ │  + color head)   │
│ Binary:        │ │  shape feats)  │ │ Multi-class:     │
│ Infected /     │ │ Multi-class:   │ │ Normal /         │
│ Uninfected     │ │ Normal /Sickle │ │ Hypo / Target /  │
│                │ │ /Target/Other  │ │ Pencil           │
└───────┬────────┘ └──────┬─────────┘ └────────┬─────────┘
        │                 │                     │
        └─────────────────┴──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ Grad-CAM Heatmaps    │
                          │ (per positive cell)  │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ Smear-Level Report   │
                          │ Aggregation Engine   │
                          └──────────┬──────────┘
                                     │
                                     ▼
                               JSON Result
```

---

### 7.1 Stage 1: Blood Cell Segmentation Module

#### 7.1.1 Model Options (switchable via config)

**Option A — YOLOv8n (Primary, Fast)**

YOLOv8n (nano variant) fine-tuned on blood cell detection datasets. Selected for:
- Inference speed: ~15ms per image on CPU
- Good mAP@0.5 ≥ 0.85 on BCCD dataset
- Single-pass detection with bounding boxes
- Excellent for dense RBC fields

Training configuration:
```yaml
model: yolov8n.pt
task: detect
classes: [RBC, WBC, Platelet]
img_size: 640
batch: 16
epochs: 100
data: blood_cell_detection.yaml
augmentation:
  hsv_h: 0.015
  hsv_s: 0.7
  hsv_v: 0.4
  degrees: 10.0
  translate: 0.1
  scale: 0.5
  fliplr: 0.5
  mosaic: 1.0
```

**Option B — SAM-Lite (Accurate, Slower)**

Meta's Segment Anything Model (lightweight) for pixel-level cell masks. Selected for:
- Superior boundary accuracy (good for shape-dependent SCD model)
- Outputs actual cell masks, not just bounding boxes
- Enables circular cell cropping (background exclusion)
- Inference: ~80ms per image on CPU (acceptable for batch mode)

#### 7.1.2 Post-Segmentation Filtering

After detection, every candidate cell ROI passes through a validation filter:

```python
class CellValidator:
    """
    Validates detected cell regions before passing to classifiers.
    Rejects: too small, too large, WBCs, platelets, cell clusters.
    """
    MIN_AREA_PX = 200        # Minimum cell area in pixels (at 100x magnification)
    MAX_AREA_PX = 8000       # Maximum — rejects clumped cells
    MIN_CIRCULARITY = 0.3    # Rejects elongated non-cell artifacts
    MAX_WBC_AREA = 15000     # White blood cells are much larger — excluded
    ASPECT_RATIO_MAX = 3.5   # Beyond this = likely artifact or sickle in extreme form

    def validate(self, cell_roi, mask) -> bool:
        area = cv2.countNonZero(mask)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * pi * area / (perimeter ** 2)
        bbox_aspect = width / height
        return (
            self.MIN_AREA_PX <= area <= self.MAX_AREA_PX
            and circularity >= self.MIN_CIRCULARITY
            and bbox_aspect <= self.ASPECT_RATIO_MAX
        )
```

#### 7.1.3 Cell Coordinate Tracking

Every detected cell is assigned a stable unique ID and its position in the original image is stored. This enables:
- Overlay rendering on the original image (click a cell → see its diagnosis)
- Spatial cluster analysis (are infected cells clustered or distributed?)
- Quality metric: cells per field (low count → low magnification warning)

---

### 7.2 Stage 2: Cell Enhancement Pipeline

Before classification, each cropped cell undergoes a standardized enhancement pipeline to normalize for:
- Stain batch variation (different labs, different Giemsa concentrations)
- Illumination non-uniformity
- Camera/microscope noise
- Focus quality variation

#### 7.2.1 Enhancement Steps (in order)

**Step 1: Resize to standard input**
```python
cell_img = cv2.resize(cell_crop, (64, 64), interpolation=cv2.INTER_LANCZOS4)
```
All classifiers expect 64×64 RGB input. Lanczos4 interpolation preserves fine structure better than bilinear for upscaling.

**Step 2: Stain Normalization — Macenko Method**
Normalizes hematoxylin-eosin or Giemsa stain concentrations to a reference stain profile. This is critical for cross-lab generalization.

```python
# Using torchstain library
normalizer = MacenkoNormalizer()
normalizer.fit(reference_image)  # Fitted once at startup
normalized = normalizer.normalize(cell_img)
```

**Step 3: CLAHE (Contrast Limited Adaptive Histogram Equalization)**
Applied to the L channel in LAB color space. Enhances fine intracellular details (ring forms, stippling) without over-amplifying noise.

```python
lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
lab[:,:,0] = clahe.apply(lab[:,:,0])
enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
```

**Step 4: Bilateral Filtering (Noise Reduction)**
Smooths noise while preserving cell edges. Applied with small kernel to avoid blurring diagnostic features.

```python
denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=30, sigmaSpace=30)
```

**Step 5: Circular Masking**
For cells segmented as circles, the background is masked out to reduce background influence on classification. This is especially important for color-based Thalassemia detection.

```python
mask = np.zeros_like(cell_img[:,:,0])
cx, cy = cell_img.shape[1]//2, cell_img.shape[0]//2
radius = min(cx, cy) - 2
cv2.circle(mask, (cx, cy), radius, 255, -1)
cell_masked = cv2.bitwise_and(cell_img, cell_img, mask=mask)
```

**Step 6: Normalization to [0, 1]**
```python
cell_tensor = torch.tensor(cell_masked).float() / 255.0
# Apply ImageNet mean/std normalization for pretrained backbone compatibility
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
cell_tensor = normalize(cell_tensor.permute(2, 0, 1))
```

---

### 7.3 Stage 3: Disease Classification Models

#### 7.3.1 Model A: Malaria Classifier

**Architecture**: EfficientNet-B0 (fine-tuned)

**Why EfficientNet-B0?**
- Excellent accuracy-to-parameter ratio (~5.3M parameters)
- Strong performance on texture classification (crucial for detecting ring forms)
- Proven in malaria cell classification literature (comparable to ResNet-50 with 3× fewer params)
- Fast inference: ~8ms/cell on CPU

**Model Architecture**:
```
EfficientNet-B0 Backbone (ImageNet pretrained, frozen layers 1-6)
    │
    ▼
Global Average Pooling (1280-dim feature vector)
    │
    ▼
Dropout(0.3)
    │
    ▼
Linear(1280 → 256)
    │
    ▼
ReLU + BatchNorm1d(256)
    │
    ▼
Dropout(0.2)
    │
    ▼
Linear(256 → 2)   [Parasitized, Uninfected]
    │
    ▼
Softmax → [P_parasitized, P_uninfected]
```

**Training Details**:
- Loss: Cross-entropy with class weighting (parasitized class weighted 1.5× due to clinical importance of false negatives)
- Optimizer: AdamW (lr=1e-4, weight_decay=1e-5)
- Scheduler: CosineAnnealingLR (T_max=50)
- Data augmentation: Random horizontal flip, random rotation ±15°, color jitter (brightness ±0.2, contrast ±0.2), random erasing (simulates stain artifacts)
- Batch size: 64
- Epochs: 100 (early stopping patience=15)
- Target metrics: Sensitivity ≥ 95%, Specificity ≥ 90%, AUC ≥ 0.97

**Output**:
```json
{
  "malaria": {
    "prediction": "parasitized",
    "confidence": 0.943,
    "probabilities": {"parasitized": 0.943, "uninfected": 0.057}
  }
}
```

---

#### 7.3.2 Model B: Sickle Cell Anemia Classifier

**Architecture**: MobileNetV3-Large + Shape Feature Fusion Head

**Why MobileNetV3-Large + Shape Features?**
- Sickle cell detection is fundamentally a shape problem
- Pure CNN features may miss subtle curvature — explicit shape descriptors help
- Shape features: circularity, aspect ratio, solidity, extent, Hu moments
- Feature fusion: CNN embedding concatenated with shape vector before final classification

**Model Architecture**:
```
Cell Image (64×64 RGB)
    │
    ├──────────────────────────────────────────────────────────┐
    │                                                          │
    ▼                                                          ▼
MobileNetV3-Large Backbone                      OpenCV Shape Extraction
(ImageNet pretrained, fine-tuned)               - Circularity
→ 960-dim embedding                             - Aspect ratio
→ AdaptiveAvgPool                               - Solidity (area/convex hull)
→ 256-dim vector                                - Extent (area/bounding box)
                                                - Hu moments (7 values)
                                                → 12-dim shape vector
    │                                                          │
    └──────────────────────┬───────────────────────────────────┘
                           │
                           ▼
                   Concat([256-dim CNN, 12-dim shape])
                           │
                           ▼
                   Linear(268 → 128) + ReLU + BN
                           │
                           ▼
                   Dropout(0.25)
                           │
                           ▼
                   Linear(128 → 4)
                           │
                           ▼
                   Softmax → [P_normal, P_sickle, P_target, P_other_abnormal]
```

**Training Details**:
- Loss: Weighted Cross-entropy (sickle class weighted 2.0×)
- Optimizer: AdamW (lr=8e-5)
- Scheduler: ReduceLROnPlateau (patience=5, factor=0.5)
- Augmentation: Random rotation 360° (sickle cells can orient any direction), elastic deformation (simulates in-vivo shape variation), stain jitter
- Shape features normalized with StandardScaler (fitted on training set)
- Batch size: 32 (smaller due to shape feature computation overhead)
- Target metrics: Sickle F1 ≥ 0.95, Normal F1 ≥ 0.97, AUC ≥ 0.98

---

#### 7.3.3 Model C: Thalassemia / IDA Classifier

**Architecture**: EfficientNet-B2 with Dual-Head (Color Head + Morphology Head)

**Why Dual-Head EfficientNet-B2?**
- Thalassemia detection requires both color information (pallor) and structural information (target cell shape)
- Dual head explicitly separates these concerns in the feature extraction stage
- EfficientNet-B2 chosen over B0 for its superior feature resolution (better for subtle hypochromia detection)

**Model Architecture**:
```
Cell Image (64×64 RGB)
    │
    ▼
EfficientNet-B2 Backbone (frozen pretrained layers 1-7)
    │
    ├────────────────────────────────────┐
    │                                    │
    ▼                                    ▼
Color Analysis Branch              Morphology Branch
(LAB color space features          (Standard EfficientNet
 + CNN features from L channel)     spatial features)
- Mean central pallor ratio         - EdgeDetect features
- L channel variance                - Gradient magnitude
- A/B channel statistics            - Texture LBP
→ Flatten → Linear(128)            → GlobalAvgPool → Linear(256)
                │                                │
                └──────────────┬─────────────────┘
                               │
                               ▼
                    Concat([128, 256]) → 384-dim
                               │
                               ▼
                    Linear(384 → 5)
                               │
                               ▼
                    Softmax → [P_normal, P_hypochromic,
                               P_target, P_pencil, P_microcytic]
```

**Key Design Decisions**:
1. **Central pallor ratio**: Computed directly as a feature — the ratio of pale pixels in the center 40% of the cell to total cell pixels. This is a clinical diagnostic criterion directly encoded as a feature.
2. **LAB color space processing**: "A" and "B" channels capture stain color shifts that correlate with hemoglobin concentration
3. **LBP (Local Binary Patterns)**: Texture descriptor that captures basophilic stippling patterns

---

### 7.4 Model Training Strategy

#### 7.4.1 Data Split Protocol
```
For each disease dataset:
├── Training Set: 70%
│   └── Used for model parameter optimization
├── Validation Set: 15%
│   └── Used for hyperparameter tuning and early stopping
└── Test Set: 15%
    └── Held out completely; evaluated only once for final reporting
```

**Stratified split** is enforced — class proportions maintained across all splits.

#### 7.4.2 Class Imbalance Handling

| Strategy | When Applied |
|----------|-------------|
| Class weighting in loss | Always applied |
| SMOTE (oversampling) | When minority class < 15% |
| Undersampling majority | When dataset > 100K samples |
| Augmentation of minority | Always — 3-5× augmentation on rare classes |
| Focal Loss | If training instability observed |

#### 7.4.3 Transfer Learning Schedule

**Phase 1 (Epochs 1–20)**: Backbone frozen. Only classifier head trained.  
**Phase 2 (Epochs 21–60)**: Unfreeze last 2 blocks of backbone. Train with LR = 1e-5.  
**Phase 3 (Epochs 61–100)**: Full fine-tuning with LR = 1e-6 (discriminative LR).

This progressive unfreezing prevents catastrophic forgetting and ensures the pretrained features are preserved early in training.

#### 7.4.4 Experiment Tracking

All experiments tracked in **MLflow** with the following logged artifacts:
- Hyperparameters (learning rate, batch size, architecture, augmentation config)
- Per-epoch training and validation loss/accuracy curves
- Confusion matrix at best validation epoch
- Final test set metrics (sensitivity, specificity, AUC, F1 per class)
- Model checkpoint (.pth file) and ONNX export

---

### 7.5 Inference Pipeline

#### 7.5.1 Production Inference Flow

```python
class InferencePipeline:
    def __init__(self, config: InferenceConfig):
        self.segmentor = YOLOv8Segmentor(config.segmentor_weights)
        self.enhancer = CellEnhancementPipeline(config.reference_image_path)
        self.malaria_model = MalariaClassifier.load(config.malaria_weights)
        self.sickle_model = SickleCellClassifier.load(config.sickle_weights)
        self.thal_model = ThalassemiaClassifier.load(config.thal_weights)
        self.grad_cam = GradCAMGenerator()

    def run(self, image_path: str, job_id: str) -> InferenceResult:
        # Step 1: Load and validate image
        img = self._load_and_validate(image_path)

        # Step 2: Global preprocessing
        img_preprocessed = self._global_preprocess(img)

        # Step 3: Cell detection
        detections = self.segmentor.detect(img_preprocessed)
        cells = self._crop_and_validate_cells(img, detections)

        if len(cells) < 50:
            return InferenceResult(status="insufficient_cells", cell_count=len(cells))

        # Step 4: Enhancement (batched for efficiency)
        enhanced_cells = self.enhancer.process_batch(cells)

        # Step 5: Classification (parallelized with ThreadPoolExecutor)
        with ThreadPoolExecutor(max_workers=3) as executor:
            malaria_future = executor.submit(self._run_malaria, enhanced_cells)
            sickle_future = executor.submit(self._run_sickle, enhanced_cells)
            thal_future = executor.submit(self._run_thal, enhanced_cells)

        malaria_results = malaria_future.result()
        sickle_results = sickle_future.result()
        thal_results = thal_future.result()

        # Step 6: Grad-CAM for high-confidence positive cells
        heatmaps = self._generate_heatmaps(cells, malaria_results, sickle_results, thal_results)

        # Step 7: Aggregate smear-level report
        report = self._aggregate_report(cells, detections, malaria_results, sickle_results, thal_results, heatmaps)

        return report
```

#### 7.5.2 Smear-Level Aggregation Logic

```python
def _aggregate_report(self, ...) -> SmearReport:
    total_cells = len(cells)
    rbc_count = len([c for c in cells if c.type == "RBC"])

    # Malaria: % of cells with ring forms
    malaria_pos_count = sum(1 for r in malaria_results if r.prediction == "parasitized")
    parasitemia_rate = malaria_pos_count / rbc_count
    malaria_severity = self._classify_parasitemia(parasitemia_rate)
    # WHO severity: <0.2% low, 0.2-5% moderate, >5% severe

    # Sickle Cell: % of cells that are sickle-shaped
    sickle_count = sum(1 for r in sickle_results if r.prediction == "sickle")
    sickle_rate = sickle_count / rbc_count
    sickle_diagnosis = "Positive" if sickle_rate > 0.05 else "Negative"
    # 5% threshold aligns with clinical screening cutoff

    # Thalassemia: % of cells showing hypochromia or target cells
    thal_abnormal = sum(1 for r in thal_results if r.prediction in ["hypochromic", "target", "pencil", "microcytic"])
    thal_rate = thal_abnormal / rbc_count
    thal_diagnosis = "Suggestive" if thal_rate > 0.10 else "Negative"

    return SmearReport(
        job_id=job_id,
        total_cells_detected=total_cells,
        rbc_count=rbc_count,
        malaria=MalariaReport(
            diagnosis=malaria_severity,
            parasitemia_rate=parasitemia_rate,
            positive_cells=malaria_pos_count,
            heatmap_urls=[h.url for h in heatmaps["malaria"]]
        ),
        sickle_cell=SickleCellReport(
            diagnosis=sickle_diagnosis,
            sickle_rate=sickle_rate,
            sickle_count=sickle_count,
            cell_type_distribution={...}
        ),
        thalassemia=ThalassemiaReport(
            diagnosis=thal_diagnosis,
            abnormal_rate=thal_rate,
            abnormal_count=thal_abnormal,
            predominant_anomaly=self._get_predominant_anomaly(thal_results)
        ),
        quality_flags=self._get_quality_flags(cells, img),
        disclaimer="AI-assisted screening only. Not for clinical diagnosis without physician review.",
        processing_time_ms=elapsed_ms
    )
```

#### 7.5.3 Grad-CAM Heatmap Generation

Gradient-weighted Class Activation Maps are generated for:
- All cells predicted positive for malaria (confidence > 0.7)
- All cells predicted as sickle (confidence > 0.8)
- Representative sample of abnormal Thalassemia cells (top 10 by confidence)

```python
class GradCAMGenerator:
    def generate(self, model, cell_tensor, target_class):
        # Hook last convolutional layer
        features = []
        gradients = []

        def forward_hook(module, input, output):
            features.append(output)

        def backward_hook(module, grad_input, grad_output):
            gradients.append(grad_output[0])

        # Register hooks on last conv layer
        target_layer = model.backbone.features[-1]
        hook_f = target_layer.register_forward_hook(forward_hook)
        hook_b = target_layer.register_backward_hook(backward_hook)

        # Forward pass
        output = model(cell_tensor.unsqueeze(0))
        model.zero_grad()

        # Backward pass for target class
        class_score = output[0, target_class]
        class_score.backward()

        # Generate heatmap
        pooled_grads = torch.mean(gradients[0], dim=[0, 2, 3])
        activation_map = features[0].squeeze(0)
        for i in range(activation_map.shape[0]):
            activation_map[i, :, :] *= pooled_grads[i]

        heatmap = torch.mean(activation_map, dim=0).detach().numpy()
        heatmap = np.maximum(heatmap, 0)
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)
        heatmap = cv2.resize(heatmap, (64, 64))

        # Overlay on original cell
        heatmap_colored = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(original_cell_rgb, 0.6, heatmap_colored, 0.4, 0)

        hook_f.remove()
        hook_b.remove()

        return overlay
```

---

## 8. Backend Architecture

### 8.1 Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Language | Python | 3.11 | Modern async support, ML ecosystem |
| Web Framework | FastAPI | 0.111 | Async-native, auto-OpenAPI docs, high performance |
| Task Queue | Celery | 5.3 | Mature, Redis-backed, supports ML jobs |
| ML Framework | PyTorch | 2.2 | Primary model training/inference |
| CV Library | OpenCV | 4.9 | Image processing pipeline |
| Object Detection | Ultralytics YOLOv8 | 8.1 | Cell segmentation |
| Database ORM | SQLAlchemy | 2.0 | Async ORM with PostgreSQL |
| Migrations | Alembic | 1.13 | Database schema versioning |
| Validation | Pydantic | 2.7 | Request/response validation |
| Auth | python-jose + passlib | — | JWT tokens, bcrypt hashing |
| Storage Client | boto3 / minio | — | S3-compatible storage |
| HTTP Client | httpx | — | Async HTTP for internal comms |
| Monitoring | prometheus-fastapi-instrumentator | — | Metrics endpoint |
| Logging | structlog | — | Structured JSON logging |

### 8.2 API Design

#### 8.2.1 REST API Endpoints

**Base URL**: `/api/v1`

---

**Authentication Endpoints**

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/auth/register` | Create new user account | No |
| POST | `/auth/login` | Login, receive JWT | No |
| POST | `/auth/refresh` | Refresh access token | Yes (refresh) |
| POST | `/auth/logout` | Invalidate token | Yes |

**Sample Request — Login**:
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "doctor@clinic.com",
  "password": "securepassword123"
}
```

**Sample Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "usr_abc123",
    "email": "doctor@clinic.com",
    "name": "Dr. Priya Sharma",
    "role": "clinician"
  }
}
```

---

**Analysis Endpoints**

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/analysis/upload` | Upload smear image, start analysis | Yes |
| GET | `/analysis/{job_id}` | Get analysis status and result | Yes |
| GET | `/analysis/{job_id}/cells` | Get per-cell breakdown | Yes |
| GET | `/analysis/{job_id}/heatmaps/{cell_id}` | Get heatmap for specific cell | Yes |
| GET | `/analysis/{job_id}/report/pdf` | Download PDF report | Yes |
| GET | `/analysis/history` | List user's past analyses | Yes |
| DELETE | `/analysis/{job_id}` | Delete analysis and images | Yes |

**POST /analysis/upload — Full Spec**:
```http
POST /api/v1/analysis/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

image: [binary file]
patient_id: "PT-2026-00123"  (optional, for record linking)
notes: "Fever for 3 days, returned from endemic region"  (optional)
```

**Response (202 Accepted)**:
```json
{
  "job_id": "job_8f3k2m1p",
  "status": "queued",
  "estimated_duration_seconds": 25,
  "websocket_url": "ws://api.hemavision.ai/ws/jobs/job_8f3k2m1p",
  "check_url": "/api/v1/analysis/job_8f3k2m1p"
}
```

**GET /analysis/{job_id} — Result Schema**:
```json
{
  "job_id": "job_8f3k2m1p",
  "status": "completed",
  "created_at": "2026-05-04T10:30:00Z",
  "completed_at": "2026-05-04T10:30:22Z",
  "processing_time_ms": 22043,
  "image": {
    "original_url": "https://storage.hemavision.ai/images/orig/job_8f3k2m1p.jpg",
    "annotated_url": "https://storage.hemavision.ai/images/annotated/job_8f3k2m1p.jpg"
  },
  "cell_statistics": {
    "total_detected": 312,
    "rbc_count": 287,
    "wbc_count": 18,
    "platelet_count": 7,
    "rejected_count": 23
  },
  "results": {
    "malaria": {
      "diagnosis": "Positive — Moderate Parasitemia",
      "confidence": 0.94,
      "parasitemia_rate": 0.078,
      "parasitized_cells": 22,
      "severity": "moderate",
      "severity_description": "7.8% parasitemia — WHO Moderate. Clinical attention recommended.",
      "species_hint": "Ring forms consistent with P. falciparum morphology"
    },
    "sickle_cell": {
      "diagnosis": "Negative",
      "confidence": 0.97,
      "sickle_rate": 0.003,
      "sickle_cells": 1,
      "cell_distribution": {
        "normal": 271,
        "sickle": 1,
        "target": 8,
        "other_abnormal": 7
      }
    },
    "thalassemia": {
      "diagnosis": "Negative",
      "confidence": 0.91,
      "abnormal_rate": 0.042,
      "abnormal_cells": 12,
      "cell_distribution": {
        "normal": 275,
        "hypochromic": 8,
        "target": 3,
        "pencil": 1,
        "microcytic": 0
      }
    }
  },
  "quality_flags": [],
  "overall_recommendation": "Malaria positive — initiate appropriate antimalarial therapy. Refer for confirmatory RDT or PCR.",
  "disclaimer": "AI-assisted screening. Not a substitute for physician diagnosis.",
  "model_versions": {
    "segmentor": "yolov8n-blood-v2.1",
    "malaria_classifier": "efficientnet-b0-malaria-v3.2",
    "sickle_classifier": "mobilenetv3-sickle-v2.0",
    "thal_classifier": "efficientnet-b2-thal-v1.5"
  }
}
```

---

**Batch Analysis Endpoints**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/batch/upload` | Upload multiple images for batch processing |
| GET | `/batch/{batch_id}` | Get batch status and aggregate results |
| GET | `/batch/{batch_id}/export` | Download batch results as CSV/JSON |

---

**Admin Endpoints** (role: admin)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/models` | List all model versions |
| POST | `/admin/models/deploy` | Deploy new model version |
| GET | `/admin/stats` | System usage statistics |
| GET | `/admin/queue` | Celery queue status |

---

#### 8.2.2 WebSocket API

WebSocket endpoint for real-time analysis progress updates.

**Endpoint**: `ws://{host}/ws/jobs/{job_id}`

**Message Schema (Server → Client)**:
```json
// Stage update
{"type": "progress", "stage": "segmentation", "progress": 0.45, "message": "Detecting blood cells..."}

// Stage completion
{"type": "stage_complete", "stage": "segmentation", "cell_count": 287, "duration_ms": 3200}

// Classifier update
{"type": "classifier_progress", "classifier": "malaria", "cells_processed": 150, "total_cells": 287}

// Final result
{"type": "complete", "job_id": "job_8f3k2m1p", "result_url": "/api/v1/analysis/job_8f3k2m1p"}

// Error
{"type": "error", "code": "LOW_CELL_COUNT", "message": "Only 23 cells detected. Minimum 50 required for reliable analysis."}
```

#### 8.2.3 Error Response Schema

```json
{
  "error": {
    "code": "INVALID_IMAGE_FORMAT",
    "message": "Uploaded file is not a valid image. Supported formats: JPG, PNG, TIFF, BMP.",
    "details": {"received_type": "application/pdf"},
    "request_id": "req_xyz789"
  }
}
```

**Error Codes Reference**:

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_IMAGE_FORMAT` | 422 | Non-image file uploaded |
| `IMAGE_TOO_SMALL` | 422 | Image below 200×200 pixels |
| `IMAGE_TOO_LARGE` | 413 | Image above 50MB |
| `LOW_CELL_COUNT` | 200 | Analysis complete but < 50 cells detected |
| `POOR_IMAGE_QUALITY` | 200 | Focus/stain quality insufficient |
| `JOB_NOT_FOUND` | 404 | Job ID doesn't exist or belongs to another user |
| `QUOTA_EXCEEDED` | 429 | User's daily analysis quota exceeded |
| `MODEL_UNAVAILABLE` | 503 | Inference service temporarily down |
| `QUEUE_FULL` | 503 | System at capacity |

---

### 8.3 Database Schema

**Database**: PostgreSQL 15

#### Table: users
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    role            VARCHAR(50) DEFAULT 'clinician',  -- clinician, researcher, admin
    institution     VARCHAR(255),
    country         VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    is_verified     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    daily_quota     INTEGER DEFAULT 50,  -- analyses per day
    CONSTRAINT role_check CHECK (role IN ('clinician', 'researcher', 'admin'))
);

CREATE INDEX idx_users_email ON users(email);
```

#### Table: analysis_jobs
```sql
CREATE TABLE analysis_jobs (
    id                  VARCHAR(50) PRIMARY KEY,  -- job_XXXXXXXX format
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status              VARCHAR(30) DEFAULT 'queued',
    -- queued, preprocessing, segmenting, enhancing, classifying, generating_report, completed, failed
    patient_id          VARCHAR(100),  -- optional, user-provided
    notes               TEXT,
    image_original_key  VARCHAR(500),  -- MinIO object key
    image_annotated_key VARCHAR(500),
    image_thumbnail_key VARCHAR(500),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    processing_time_ms  INTEGER,
    error_code          VARCHAR(100),
    error_message       TEXT,
    celery_task_id      VARCHAR(255),
    CONSTRAINT status_check CHECK (status IN ('queued','preprocessing','segmenting','enhancing','classifying','generating_report','completed','failed'))
);

CREATE INDEX idx_jobs_user ON analysis_jobs(user_id);
CREATE INDEX idx_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_jobs_created ON analysis_jobs(created_at DESC);
```

#### Table: smear_statistics
```sql
CREATE TABLE smear_statistics (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id              VARCHAR(50) NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE UNIQUE,
    total_cells         INTEGER,
    rbc_count           INTEGER,
    wbc_count           INTEGER,
    platelet_count      INTEGER,
    rejected_count      INTEGER,
    image_width         INTEGER,
    image_height        INTEGER,
    magnification_hint  VARCHAR(20),  -- 40x, 100x, unknown
    stain_quality_score FLOAT,        -- 0-1
    focus_quality_score FLOAT,        -- 0-1
    cells_per_field     FLOAT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

#### Table: disease_results
```sql
CREATE TABLE disease_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          VARCHAR(50) NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
    disease         VARCHAR(30) NOT NULL,  -- malaria, sickle_cell, thalassemia
    diagnosis       VARCHAR(100),
    confidence      FLOAT,
    positive_rate   FLOAT,
    positive_count  INTEGER,
    total_analyzed  INTEGER,
    severity        VARCHAR(50),   -- for malaria: low/moderate/severe
    raw_distribution JSONB,        -- full cell-type distribution
    model_version   VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(job_id, disease)
);

CREATE INDEX idx_disease_results_job ON disease_results(job_id);
```

#### Table: cell_detections
```sql
CREATE TABLE cell_detections (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id              VARCHAR(50) NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
    cell_index          INTEGER NOT NULL,   -- order in which detected
    cell_type           VARCHAR(20),        -- RBC, WBC, Platelet
    bbox_x              INTEGER,
    bbox_y              INTEGER,
    bbox_w              INTEGER,
    bbox_h              INTEGER,
    area_px             INTEGER,
    circularity         FLOAT,
    aspect_ratio        FLOAT,
    cell_crop_key       VARCHAR(500),       -- MinIO key for individual cell image
    heatmap_key         VARCHAR(500),       -- MinIO key for Grad-CAM overlay (if generated)
    malaria_prediction  VARCHAR(30),
    malaria_confidence  FLOAT,
    sickle_prediction   VARCHAR(30),
    sickle_confidence   FLOAT,
    thal_prediction     VARCHAR(30),
    thal_confidence     FLOAT,
    is_flagged          BOOLEAN DEFAULT FALSE,  -- manually flagged for review
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cells_job ON cell_detections(job_id);
CREATE INDEX idx_cells_malaria ON cell_detections(job_id, malaria_prediction);
CREATE INDEX idx_cells_sickle ON cell_detections(job_id, sickle_prediction);
```

#### Table: model_versions
```sql
CREATE TABLE model_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) UNIQUE NOT NULL,  -- e.g. "efficientnet-b0-malaria-v3.2"
    disease         VARCHAR(30),
    architecture    VARCHAR(100),
    version         VARCHAR(20),
    weights_path    VARCHAR(500),  -- path on model storage
    is_active       BOOLEAN DEFAULT FALSE,
    test_accuracy   FLOAT,
    test_auc        FLOAT,
    test_sensitivity FLOAT,
    test_specificity FLOAT,
    training_dataset VARCHAR(255),
    training_samples INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    deployed_at     TIMESTAMPTZ
);
```

#### Table: audit_log
```sql
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100),
    resource_type   VARCHAR(50),
    resource_id     VARCHAR(100),
    ip_address      INET,
    user_agent      TEXT,
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_log(action, created_at DESC);
```

---

### 8.4 File Storage

**Technology**: MinIO (self-hosted, S3-compatible)

**Bucket Structure**:
```
hemavision-storage/
├── images/
│   ├── original/         # Raw uploaded smear images
│   │   └── {job_id}/original.jpg
│   ├── annotated/        # Full smear with bounding box overlays
│   │   └── {job_id}/annotated.jpg
│   └── thumbnails/       # 256×256 thumbnails for history view
│       └── {job_id}/thumb.jpg
│
├── cells/
│   ├── crops/            # Individual cell crop images (64×64)
│   │   └── {job_id}/{cell_index}.png
│   └── heatmaps/         # Grad-CAM overlays on cells
│       └── {job_id}/{cell_index}_{disease}.png
│
├── reports/
│   └── {job_id}/report.pdf    # Generated PDF reports
│
└── models/
    ├── segmentor/
    │   └── yolov8n-blood-v2.1.pt
    ├── malaria/
    │   └── efficientnet-b0-malaria-v3.2.pth
    ├── sickle/
    │   └── mobilenetv3-sickle-v2.0.pth
    └── thalassemia/
        └── efficientnet-b2-thal-v1.5.pth
```

**Retention Policy**:
- Original images: 90 days (configurable)
- Cell crops: 30 days
- Reports: 1 year
- Model weights: Permanent

**Access Control**:
- Images only accessible via pre-signed URLs (15-minute expiry)
- Model weights bucket: Read-only for application service accounts
- Public access: Disabled on all buckets

---

### 8.5 Queue & Job Management

**Technology**: Celery 5.3 with Redis 7 backend and broker

```python
# celery_app.py
from celery import Celery

celery_app = Celery(
    "hemavision",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["app.tasks.analysis"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,          # Re-queue on worker crash
    worker_prefetch_multiplier=1,  # One job at a time per worker (ML is memory-heavy)
    task_routes={
        "analysis.run_inference": {"queue": "gpu"},      # GPU queue if available
        "analysis.generate_report": {"queue": "default"},
        "analysis.cleanup": {"queue": "low_priority"},
    },
    beat_schedule={
        # Cleanup old temp files daily at 2 AM
        "cleanup-temp-files": {
            "task": "analysis.cleanup_temp",
            "schedule": crontab(hour=2, minute=0),
        },
    }
)
```

**Job Lifecycle**:
```
User uploads → API creates DB record (status=queued) → Push to Celery queue
→ Worker picks up → status=preprocessing
→ Status updates sent via Redis pub/sub → WebSocket broadcasts to client
→ Inference complete → status=completed, result stored in DB
→ Client receives WebSocket complete message → Frontend updates UI
```

---

### 8.6 Authentication & Security

**Authentication**: JWT (access token: 1 hour, refresh: 7 days)

```python
# JWT payload structure
{
  "sub": "usr_abc123",       # User ID
  "email": "dr@clinic.com",
  "role": "clinician",
  "iat": 1746348000,
  "exp": 1746351600,
  "jti": "unique-token-id"   # For token revocation
}
```

**Security Measures**:

| Measure | Implementation |
|---------|----------------|
| Password hashing | bcrypt, cost factor 12 |
| SQL injection | SQLAlchemy parameterized queries only |
| XSS | CSP headers, no raw HTML rendering |
| CSRF | Double-submit cookie pattern for form submissions |
| Rate limiting | slowapi middleware: 60 req/min general, 10 uploads/hour |
| Image validation | Magic bytes check + PIL verification before processing |
| Input size limit | Max 50MB per upload, max 10 images per batch |
| HTTPS | Enforced via Nginx redirect |
| CORS | Whitelist specific frontend origins |
| Secrets management | Environment variables via Docker secrets / .env |
| Audit logging | All analysis and auth actions logged to audit_log table |
| PII handling | Patient IDs optional; images purged per retention policy |

---

## 9. Frontend Architecture

### 9.1 Tech Stack & Design System

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.3 | UI framework |
| TypeScript | 5.4 | Type safety |
| Vite | 5.3 | Build tool |
| Tailwind CSS | 3.4 | Utility-first styling |
| shadcn/ui | latest | Accessible component primitives |
| Framer Motion | 11 | Animations |
| React Query | 5 | Server state management |
| Zustand | 4.5 | Client state management |
| React Router | 6 | Client-side routing |
| Recharts | 2.12 | Data visualization charts |
| React Dropzone | 14 | Drag-and-drop file upload |
| fabric.js | 6 | Interactive canvas for cell annotation overlay |
| jsPDF | 2.5 | Client-side PDF generation (supplementary) |
| axios | 1.7 | HTTP client |
| socket.io-client | 4.7 | WebSocket client |

**Design System — HemaVision UI Kit**:

```css
/* Design Tokens */
:root {
  /* Primary palette — pure white to light sky blue gradient */
  --color-bg-base: #FFFFFF;
  --color-bg-subtle: #F0F8FF;        /* Alice Blue */
  --color-bg-muted: #E1F0FA;         /* Lightest sky */
  --color-surface: #FFFFFF;
  --color-surface-elevated: #F7FBFF;

  /* Sky blue spectrum */
  --color-sky-50:  #F0F9FF;
  --color-sky-100: #E0F2FE;
  --color-sky-200: #BAE6FD;
  --color-sky-300: #7DD3FC;
  --color-sky-400: #38BDF8;
  --color-sky-500: #0EA5E9;          /* Primary interactive */
  --color-sky-600: #0284C7;          /* Hover state */
  --color-sky-700: #0369A1;          /* Active state */

  /* Clinical accent colors */
  --color-malaria:  #EF4444;         /* Red — critical alert */
  --color-sickle:   #F97316;         /* Orange — warning */
  --color-thal:     #EAB308;         /* Amber — attention */
  --color-negative: #22C55E;         /* Green — all clear */
  --color-uncertain:#94A3B8;         /* Slate — needs review */

  /* Text */
  --color-text-primary:   #0F172A;   /* Near-black for max contrast */
  --color-text-secondary: #475569;
  --color-text-muted:     #94A3B8;
  --color-text-on-primary:#FFFFFF;

  /* Typography */
  --font-display: 'DM Serif Display', Georgia, serif;   /* Headers */
  --font-body:    'DM Sans', system-ui, sans-serif;      /* Body text */
  --font-mono:    'JetBrains Mono', monospace;           /* Code/IDs */
  --font-medical: 'Source Serif 4', Georgia, serif;      /* Clinical data */

  /* Spacing scale */
  --spacing-xs:  4px;
  --spacing-sm:  8px;
  --spacing-md:  16px;
  --spacing-lg:  24px;
  --spacing-xl:  32px;
  --spacing-2xl: 48px;

  /* Border radius */
  --radius-sm:  6px;
  --radius-md:  12px;
  --radius-lg:  16px;
  --radius-xl:  24px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm:  0 1px 3px rgba(14, 165, 233, 0.08), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md:  0 4px 16px rgba(14, 165, 233, 0.12), 0 2px 8px rgba(0,0,0,0.08);
  --shadow-lg:  0 10px 40px rgba(14, 165, 233, 0.16), 0 4px 16px rgba(0,0,0,0.10);
  --shadow-glow: 0 0 24px rgba(14, 165, 233, 0.25);

  /* Gradients */
  --gradient-hero: linear-gradient(135deg, #FFFFFF 0%, #E0F2FE 40%, #BAE6FD 100%);
  --gradient-card: linear-gradient(160deg, #FFFFFF 0%, #F0F9FF 100%);
  --gradient-button: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
  --gradient-malaria: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
  --gradient-negative: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
}
```

---

### 9.2 Page & Screen Specifications

#### Screen 1: Landing / Home Page

**URL**: `/`

**Purpose**: Convert visitors, explain the product, demo capability.

**Layout**: Full-page scroll with these sections:
1. **Hero Section**: Animated blood cell illustration (SVG, animated with CSS), headline, CTA button ("Analyze a Smear — Free")
2. **How It Works**: 3-step process visualization (Upload → Analyze → Report)
3. **Disease Coverage**: Cards for each of the 3 diseases with visual cell illustrations
4. **Accuracy Stats**: Key metrics (97% AUC, 22s avg time, 300+ cells analyzed per smear)
5. **Sample Report Preview**: Interactive mockup showing result UI
6. **CTA Section**: Register or login

**Design Notes**:
- Background: `var(--gradient-hero)` applied as a full-page mesh gradient
- Animated floating cell particles in hero (3–5 circular SVGs drifting slowly)
- Typography: Display font for headlines, DM Sans for body
- No dark sections — all white to sky blue gradient sections

---

#### Screen 2: Authentication (Login / Register)

**URL**: `/auth`

**Layout**: Split screen
- Left: Large illustration of microscope + blood cells (SVG)
- Right: Auth form (tab-switched between Login and Register)

**Form Fields (Register)**:
- Full name
- Email
- Password + confirm
- Institution (optional)
- Role: Clinician / Researcher / Student
- Country

**Validation**: Real-time with Zod schema, inline error messages.

---

#### Screen 3: Dashboard (Main App)

**URL**: `/dashboard`

**Layout**: Sidebar navigation + main content area

**Sidebar Links**:
- Dashboard (home)
- New Analysis
- History
- Batch Upload
- Settings
- Help

**Dashboard Content**:
- **Stats bar**: Total analyses, Malaria detected, Sickle cell detected, Thalassemia detected (animated counters)
- **Recent Analyses**: Table with last 10 jobs, status badges, quick-view buttons
- **Usage Graph**: Line chart (Recharts) of analyses per day, last 30 days
- **Quick Upload Zone**: Drop-here card at top of content area

---

#### Screen 4: New Analysis — Upload

**URL**: `/analysis/new`

**Layout**: Centered, clean form

**Components**:
1. **Drop Zone**: Large card (400×300px) with dashed border that accepts drag-and-drop or file picker
   - Accepted formats: JPG, PNG, TIFF, BMP
   - Max size: 50MB
   - Preview thumbnail shows on selection
   - Animated upload progress bar
2. **Metadata Fields**: Patient ID (optional), clinical notes (optional)
3. **Submit Button**: "Analyze Blood Smear" — disabled until valid image selected

**Image Validation (Client-side)**:
- File type check
- File size check (< 50MB)
- Image dimension check (> 200×200)
- Preview generation

---

#### Screen 5: Analysis In Progress

**URL**: `/analysis/{job_id}/processing`

**Layout**: Centered progress display

**Components**:
1. **Stage Progress Tracker**: Visual step-by-step indicator
   ```
   ✅ Image Uploaded
   ✅ Preprocessing
   🔄 Detecting Blood Cells...  [━━━━━━━━━░░░░░░░░░░░ 45%]
   ○ Enhancing Cells
   ○ Malaria Analysis
   ○ Sickle Cell Analysis
   ○ Thalassemia Analysis
   ○ Generating Report
   ```
2. **Live Cell Counter**: "237 cells detected so far..." (updated via WebSocket)
3. **Animated Microscope Graphic**: SVG animation of cells being analyzed
4. **Estimated Time**: Countdown timer

**WebSocket integration**: Socket.io client subscribes to job room, updates stage tracker in real-time.

---

#### Screen 6: Analysis Results

**URL**: `/analysis/{job_id}`

**Layout**: Multi-section page with tabs

**Section 1: Summary Banner**
- Overall status chip (e.g., "🔴 Malaria Detected — Moderate Parasitemia")
- Key stats: Total cells, processing time, image quality
- Actions: Download PDF, Share Link, Delete

**Section 2: Disease Result Cards (3 cards)**

Each card contains:
- Disease name + icon
- Diagnosis badge (Positive/Negative/Suspicious)
- Confidence meter (animated arc gauge)
- Key stat (e.g., "7.8% parasitemia rate")
- Cell distribution donut chart (Recharts)
- Expandable details section

**Card Visual States**:
- Negative: `var(--gradient-negative)` background, green checkmark
- Positive: `var(--gradient-malaria)` background, red alert icon
- Suspicious: Amber gradient background, warning icon

**Section 3: Interactive Cell Map**

Full-width canvas (fabric.js) showing:
- Original annotated smear image
- Colored bounding boxes per cell (red=malaria+, orange=sickle, yellow=thal abnormal, green=normal)
- Click any cell → panel opens showing:
  - Cell crop (enlarged)
  - Grad-CAM heatmap overlay
  - Classification confidence for all 3 diseases
  - Cell morphological metrics (area, circularity, aspect ratio)

**Section 4: Cell Gallery (Tabs)**

Tabbed view:
- Tab "All Cells": Grid of cell thumbnails with mini-badges
- Tab "Malaria Positive": Only parasitized cells, with heatmaps
- Tab "Sickle Cells": Sickle/abnormal cells, sorted by confidence
- Tab "Thal Abnormal": Hypochromic/target cells

Each cell card in gallery: thumbnail + predicted class + confidence score + click to expand

**Section 5: Recommendations**

Clinical narrative block (light blue card):
- Auto-generated recommendation text based on diagnosis results
- Disclaimer about AI-assisted nature of results
- Links to WHO clinical guidelines for each detected disease
- Next steps checklist

---

#### Screen 7: Analysis History

**URL**: `/history`

**Layout**: Table + filters

**Features**:
- Search by patient ID, date, disease
- Filter by disease detected, date range, status
- Sort by date, processing time
- Pagination (20 per page)
- Bulk delete option
- Export history as CSV

---

#### Screen 8: Batch Upload

**URL**: `/batch`

**Features**:
- Multi-file drop zone (up to 20 images)
- Per-file status tracking
- Batch-level summary stats
- Export batch results as CSV

---

### 9.3 Component Library

**Atomic Components** (built on shadcn/ui primitives):

```
components/
├── ui/                          # shadcn/ui base components
│   ├── button.tsx
│   ├── card.tsx
│   ├── badge.tsx
│   ├── dialog.tsx
│   ├── tabs.tsx
│   ├── progress.tsx
│   └── ...
│
├── analysis/
│   ├── UploadDropzone.tsx        # File drag/drop with validation
│   ├── AnalysisProgress.tsx      # Real-time stage tracker
│   ├── DiseaseResultCard.tsx     # Individual disease result card
│   ├── CellCanvas.tsx            # fabric.js interactive cell map
│   ├── CellGallery.tsx           # Grid of individual cell images
│   ├── CellDetailPanel.tsx       # Slide-in panel for cell details
│   ├── HeatmapOverlay.tsx        # Grad-CAM visualization
│   ├── ConfidenceGauge.tsx       # Arc gauge for confidence score
│   ├── CellDistributionChart.tsx # Recharts donut for cell types
│   ├── QualityBadge.tsx          # Image quality indicator
│   └── RecommendationCard.tsx    # Clinical recommendation block
│
├── dashboard/
│   ├── StatsBar.tsx              # Animated counter stats
│   ├── RecentAnalysesTable.tsx   # Last 10 analyses table
│   ├── UsageChart.tsx            # Daily analyses line chart
│   └── QuickUpload.tsx           # Small upload card for dashboard
│
├── layout/
│   ├── Sidebar.tsx               # Navigation sidebar
│   ├── TopBar.tsx                # Page header + user menu
│   ├── PageContainer.tsx         # Standard page wrapper
│   └── EmptyState.tsx            # Empty state component
│
└── common/
    ├── LoadingSpinner.tsx
    ├── ErrorBoundary.tsx
    ├── ConfirmDialog.tsx
    ├── Tooltip.tsx
    └── StatusBadge.tsx
```

---

### 9.4 State Management

**React Query** — Server state (API calls, caching):
```typescript
// Example: Analysis result query with auto-refetch until complete
const { data: analysisResult, isLoading } = useQuery({
  queryKey: ['analysis', jobId],
  queryFn: () => api.getAnalysis(jobId),
  refetchInterval: (data) => {
    if (data?.status === 'completed' || data?.status === 'failed') return false
    return 5000  // Poll every 5s while job is running
  },
  staleTime: 1000 * 60 * 5,  // 5 minutes
})
```

**Zustand** — Client state (UI state, WebSocket data):
```typescript
interface AppStore {
  // Upload state
  uploadedFile: File | null
  uploadPreview: string | null

  // WebSocket state
  jobProgress: JobProgress | null
  wsConnected: boolean

  // UI state
  selectedCellId: string | null
  activeDiseaseTab: 'malaria' | 'sickle' | 'thalassemia' | 'all'
  cellGalleryFilter: string

  // Actions
  setUploadedFile: (file: File | null) => void
  setJobProgress: (progress: JobProgress) => void
  setSelectedCellId: (id: string | null) => void
}
```

---

### 9.5 UI/UX Guidelines

**Interaction Principles**:

1. **Progressive Disclosure**: Complex data (per-cell breakdown, heatmaps) hidden behind expand/click actions. Summary-first design.
2. **Optimistic Updates**: UI updates immediately on user action; rolls back on API error.
3. **Real-time Feedback**: WebSocket progress for all analysis jobs. No silent waiting.
4. **Error Recovery**: Every error state includes a clear action ("Retry", "Contact Support", "Upload Different Image").
5. **Accessibility**: All interactive elements keyboard-navigable. WCAG 2.1 AA compliance. ARIA labels on clinical data.

**Color Usage in Clinical Context**:
- Red variants (`--color-malaria`) used ONLY for positive/critical findings — never decoratively
- Green (`--color-negative`) used ONLY for confirmed negative results
- Amber/orange for suspicious/borderline results
- Sky blue for neutral UI elements, buttons, borders, backgrounds

**Typography Hierarchy**:
- Page titles: DM Serif Display, 32px, weight 400
- Section headings: DM Sans, 20px, weight 600
- Clinical values: Source Serif 4, 18px (distinguishes medical data from UI text)
- Body text: DM Sans, 14px, weight 400
- Labels/badges: DM Sans, 12px, weight 500, uppercase tracking

**Animation Guidelines**:
- Page transitions: 200ms ease-out fade + slide
- Card reveals: Staggered entrance (50ms delay between cards)
- Progress bars: Spring animation, not linear fill
- Number counters: Animated count-up (1200ms, easeOut)
- Heatmap reveals: Fade in over 300ms with blur-to-clear effect

---

## 10. Data Engineering & Datasets

### 10.1 Dataset Sources

| Dataset | Disease | Samples | Format | License |
|---------|---------|---------|--------|---------|
| NIH Malaria Cell Images | Malaria | 27,558 cells | PNG 150×150 | CC0 |
| Kaggle Malaria Dataset | Malaria | 27,558 cells | PNG | CC0 (mirror) |
| BCCD Dataset | Cell detection | 364 smear images | JPG + XML | MIT |
| Chula RBC-12 | Thalassemia + SCD | 49,098 cells | PNG | CC BY 4.0 |
| LISC Dataset | WBC classification | 400 WBC images | BMP | Academic |
| SCD-dataset (Erasmus MC) | Sickle Cell | ~1,500 cells | PNG | Academic |
| ArcticAI SickleCell | Sickle Cell | 3,000+ cells | PNG | Open |

### 10.2 Data Preprocessing Pipeline

```
Raw Dataset
    │
    ▼
1. Format standardization (all to PNG, RGB)
    │
    ▼
2. Resolution normalization (rescale to 100× equivalent magnification)
    │
    ▼
3. Quality filtering (remove out-of-focus, heavily artifacted images)
    │
    ▼
4. Stain normalization (Macenko) — align to reference stain
    │
    ▼
5. Label validation (cross-check annotations, remove ambiguous)
    │
    ▼
6. Class balancing check → apply SMOTE if needed
    │
    ▼
7. Stratified train/val/test split (70/15/15)
    │
    ▼
8. Augmentation pipeline definition (offline for heavy augmentation)
    │
    ▼
9. Save to HDF5 (for fast loading during training)
```

### 10.3 Data Augmentation Spec

**Augmentation techniques and intensities per disease**:

| Transform | Malaria | Sickle Cell | Thalassemia |
|-----------|---------|-------------|-------------|
| Horizontal flip | p=0.5 | p=0.5 | p=0.5 |
| Vertical flip | p=0.3 | p=0.5 | p=0.3 |
| Rotation (±15°) | p=0.7 | p=1.0 (full 360°) | p=0.7 |
| Color jitter (brightness ±0.2) | p=0.5 | p=0.3 | p=0.7 |
| Color jitter (contrast ±0.2) | p=0.5 | p=0.2 | p=0.8 |
| Gaussian noise σ=0.02 | p=0.3 | p=0.2 | p=0.3 |
| Elastic deformation | p=0.0 | p=0.5 | p=0.0 |
| Random erasing | p=0.2 | p=0.1 | p=0.1 |
| Stain jitter | p=0.5 | p=0.4 | p=0.6 |
| Zoom (0.9–1.1×) | p=0.4 | p=0.4 | p=0.4 |
| Shear (±5°) | p=0.2 | p=0.4 | p=0.2 |

---

## 11. Model Training Infrastructure

### 11.1 Training Environment

**Recommended Hardware**:
- GPU: NVIDIA RTX 3080 or better (16GB+ VRAM)
- CPU: 8+ cores for data loading workers
- RAM: 32GB
- Storage: 100GB SSD for datasets and checkpoints

**Cloud Alternative**:
- Google Colab Pro+ (A100 GPU)
- Kaggle GPU (T4, 20 hours/week free)
- Vast.ai (RTX 3090 spot instance for training runs)

### 11.2 Training Script Structure

```
training/
├── configs/
│   ├── malaria_config.yaml
│   ├── sickle_config.yaml
│   └── thal_config.yaml
├── datasets/
│   ├── malaria_dataset.py
│   ├── sickle_dataset.py
│   └── thal_dataset.py
├── models/
│   ├── malaria_model.py
│   ├── sickle_model.py
│   └── thal_model.py
├── losses/
│   ├── focal_loss.py
│   └── weighted_ce.py
├── trainers/
│   ├── base_trainer.py
│   ├── malaria_trainer.py
│   ├── sickle_trainer.py
│   └── thal_trainer.py
├── evaluation/
│   ├── metrics.py        # Sensitivity, specificity, AUC, F1
│   ├── confusion_matrix.py
│   └── calibration.py   # Platt scaling for probability calibration
├── export/
│   ├── export_onnx.py
│   └── export_torchscript.py
└── train.py             # Main entry point
```

### 11.3 MLflow Experiment Tracking

```python
import mlflow

with mlflow.start_run(run_name=f"malaria_efficientnet_b0_{timestamp}"):
    mlflow.log_params({
        "architecture": "EfficientNet-B0",
        "optimizer": "AdamW",
        "learning_rate": 1e-4,
        "batch_size": 64,
        "epochs": 100,
        "augmentation": "standard_malaria_v1"
    })

    for epoch in range(config.epochs):
        train_loss, train_acc = trainer.train_epoch()
        val_loss, val_acc, val_auc = trainer.validate_epoch()

        mlflow.log_metrics({
            "train_loss": train_loss,
            "train_accuracy": train_acc,
            "val_loss": val_loss,
            "val_accuracy": val_acc,
            "val_auc": val_auc
        }, step=epoch)

    # Final test evaluation
    test_metrics = trainer.evaluate_test_set()
    mlflow.log_metrics(test_metrics)

    # Log model artifact
    mlflow.pytorch.log_model(model, "model")
    mlflow.log_artifact("confusion_matrix.png")
    mlflow.log_artifact("roc_curve.png")
```

---

## 12. Deployment Architecture

### 12.1 Docker Compose (Development & Demo)

```yaml
# docker-compose.yml
version: '3.9'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: hemavision
      POSTGRES_USER: hemavision
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hemavision"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  # MinIO Object Storage
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  # FastAPI Backend
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://hemavision:${POSTGRES_PASSWORD}@db:5432/hemavision
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      JWT_SECRET: ${JWT_SECRET}
      MODEL_DIR: /app/models
      ENVIRONMENT: development
    volumes:
      - ./models:/app/models:ro
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://hemavision:${POSTGRES_PASSWORD}@db:5432/hemavision
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      MODEL_DIR: /app/models
    volumes:
      - ./models:/app/models:ro
      - ./backend:/app
    depends_on:
      - db
      - redis
    command: celery -A app.celery_app worker --loglevel=info --concurrency=2

  # Celery Beat (scheduler)
  beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery_app beat --loglevel=info
    depends_on:
      - redis

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: http://localhost:8000/api/v1
        VITE_WS_URL: ws://localhost:8000/ws
    ports:
      - "3000:80"
    depends_on:
      - api

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
      - frontend

  # MLflow (development only)
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    command: mlflow server --host 0.0.0.0 --port 5000
    volumes:
      - mlflow_data:/mlflow
    ports:
      - "5000:5000"

volumes:
  postgres_data:
  redis_data:
  minio_data:
  mlflow_data:
```

### 12.2 Backend Dockerfile

```dockerfile
FROM python:3.11-slim-bookworm

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
```

### 12.3 Production Deployment (Cloud)

**Recommended Cloud Stack** (cost-optimized for hackathon):

| Service | Provider | Purpose |
|---------|---------|---------|
| App hosting | Railway / Render / Fly.io | API + Worker containers |
| Database | Supabase / Neon | Managed PostgreSQL |
| Redis | Upstash | Managed Redis |
| Object Storage | Cloudflare R2 | S3-compatible, cheap egress |
| CDN | Cloudflare | Frontend static assets |
| Frontend | Vercel | React app hosting |
| Monitoring | Grafana Cloud (free) | Metrics |
| Error tracking | Sentry (free tier) | Error alerting |

**Domain Architecture**:
```
hemavision.ai                → Vercel (React frontend)
api.hemavision.ai            → Fly.io (FastAPI)
storage.hemavision.ai        → Cloudflare R2
```

---

## 13. Testing Strategy

### 13.1 AI Model Testing

**Unit Tests — Model Inference**:
```python
class TestMalariaClassifier:
    def test_parasitized_cell_correctly_classified(self, sample_parasitized_cell):
        result = classifier.predict(sample_parasitized_cell)
        assert result.prediction == "parasitized"
        assert result.confidence > 0.7

    def test_normal_cell_correctly_classified(self, sample_normal_cell):
        result = classifier.predict(sample_normal_cell)
        assert result.prediction == "uninfected"
        assert result.confidence > 0.8

    def test_output_probabilities_sum_to_one(self, any_cell):
        result = classifier.predict(any_cell)
        assert abs(sum(result.probabilities.values()) - 1.0) < 1e-6

    def test_handles_blank_image(self, blank_white_image):
        result = classifier.predict(blank_white_image)
        assert result.confidence < 0.6  # Should be low confidence
```

**Performance Tests — Benchmark**:
```python
def test_inference_speed_single_cell():
    start = time.time()
    classifier.predict(sample_cell)
    elapsed = time.time() - start
    assert elapsed < 0.05  # 50ms per cell max

def test_batch_inference_100_cells():
    start = time.time()
    classifier.predict_batch(sample_cells_100)
    elapsed = time.time() - start
    assert elapsed < 5.0  # 5 seconds for 100 cells max
```

**Held-Out Test Set Evaluation**:
Run on completely unseen test set before any production deployment. Must pass:
- Malaria: Sensitivity ≥ 95%, Specificity ≥ 90%, AUC ≥ 0.97
- Sickle Cell: Sickle F1 ≥ 0.95, Overall accuracy ≥ 94%
- Thalassemia: Abnormal detection F1 ≥ 0.88, AUC ≥ 0.93

### 13.2 Backend API Testing

**Tools**: pytest + httpx (async test client)

**Test Categories**:

| Category | Coverage Target |
|----------|----------------|
| Authentication flows | 100% |
| File upload validation | 100% |
| Analysis lifecycle (queue → complete) | 100% |
| Error responses | 90% |
| Rate limiting | 100% |
| Database CRUD operations | 95% |
| WebSocket messages | 90% |

**Integration Test — Full Analysis Flow**:
```python
@pytest.mark.asyncio
async def test_full_analysis_flow(client, sample_blood_smear_image):
    # Login
    login_resp = await client.post("/auth/login", json=credentials)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload image
    files = {"image": ("test.jpg", sample_blood_smear_image, "image/jpeg")}
    upload_resp = await client.post("/analysis/upload", files=files, headers=headers)
    assert upload_resp.status_code == 202
    job_id = upload_resp.json()["job_id"]

    # Wait for completion (test environment uses synchronous task execution)
    for _ in range(60):
        result = await client.get(f"/analysis/{job_id}", headers=headers)
        if result.json()["status"] == "completed":
            break
        await asyncio.sleep(1)

    # Validate result structure
    data = result.json()
    assert data["status"] == "completed"
    assert "malaria" in data["results"]
    assert "sickle_cell" in data["results"]
    assert "thalassemia" in data["results"]
    assert data["cell_statistics"]["total_detected"] >= 50
```

### 13.3 Frontend Testing

**Tools**: Vitest + React Testing Library + Playwright (E2E)

**Unit Tests**:
- Component rendering tests for all 20+ custom components
- Zustand store action tests
- React Query cache behavior tests
- Utility function tests (formatting, validation)

**E2E Tests (Playwright)**:
```
tests/e2e/
├── auth.spec.ts          # Login/register/logout
├── upload.spec.ts        # File upload, validation, error states
├── analysis.spec.ts      # Full analysis flow, results display
├── history.spec.ts       # History page, search, filter
└── batch.spec.ts         # Batch upload flow
```

### 13.4 Load Testing

**Tool**: Locust

**Scenarios**:
- 100 concurrent users uploading images simultaneously
- 500 concurrent API requests for analysis status
- WebSocket stress test: 1000 concurrent connections

**Success Criteria**:
- P95 API response time < 500ms (excluding analysis processing)
- Zero analysis job loss under 100 concurrent uploads
- WebSocket message latency < 100ms at 500 concurrent connections

---

## 14. Performance Benchmarks & KPIs

### 14.1 System Performance Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| End-to-end inference time | < 30 seconds | P95 over 100 test smears |
| Cell segmentation speed | < 5 seconds | YOLOv8 on 100× smear |
| Per-cell classification | < 50ms | Single cell, CPU |
| Batch inference (100 cells) | < 5 seconds | Batched forward pass |
| PDF report generation | < 3 seconds | ReportLab benchmark |
| API response time (non-ML) | < 200ms | P99 |
| WebSocket message latency | < 100ms | Redis pub/sub |
| System uptime | ≥ 99.5% | Monthly |
| Concurrent analyses | ≥ 10 simultaneous | Celery worker pool |

### 14.2 Clinical Accuracy KPIs

| Disease | Metric | Minimum Target | Stretch Target |
|---------|--------|---------------|----------------|
| Malaria | Sensitivity | 95% | 98% |
| Malaria | Specificity | 90% | 95% |
| Malaria | AUC | 0.97 | 0.99 |
| Sickle Cell | Sickle F1 | 95% | 98% |
| Sickle Cell | Overall AUC | 0.97 | 0.99 |
| Thalassemia | Abnormal F1 | 88% | 93% |
| Thalassemia | AUC | 0.93 | 0.96 |
| Segmentation | RBC detection mAP@0.5 | 85% | 90% |

### 14.3 Business KPIs (Post-launch)

| KPI | 1-Month Target | 3-Month Target |
|-----|---------------|----------------|
| Registered users | 100 | 500 |
| Total analyses | 500 | 5,000 |
| DAU | 10 | 50 |
| Analysis success rate | ≥ 95% | ≥ 97% |
| User-reported accuracy satisfaction | ≥ 4.0/5.0 | ≥ 4.3/5.0 |

---

## 15. Ethical Considerations & Compliance

### 15.1 Clinical Disclaimer

HemaVision is an **AI-assisted screening tool**, not a diagnostic device. All result screens must prominently display:

> "⚠️ HemaVision provides AI-assisted analysis for screening purposes only. Results must be reviewed by a qualified medical professional before any clinical decision is made. This tool does not replace laboratory diagnosis, clinical examination, or physician judgment."

### 15.2 Data Privacy & Anonymization

1. **Patient ID is optional**: System works without any PII
2. **Image purge**: Original images deleted after 90 days (configurable per institution)
3. **No data sharing**: Patient data never sent to third-party services
4. **Anonymized analytics**: Only aggregate usage metrics collected
5. **Data residency**: On-premise deployment option for hospitals requiring data sovereignty
6. **GDPR/DPDP compliance**: Right to deletion implemented; all PII in audit logs scrubbed after 1 year

### 15.3 Model Bias Considerations

**Known biases and mitigations**:

| Bias Type | Risk | Mitigation |
|-----------|------|-----------|
| Stain variability | Training data from specific labs may not generalize | Macenko normalization + diverse dataset sourcing |
| Magnification | Models trained at specific magnification | Documented assumption + input quality checker |
| Geographic distribution | Most datasets from specific regions | Note in model card; validate on local data |
| Camera quality | High-quality training images vs real-world low-res | Augment with synthetic degradation |
| Comorbidities | Single-disease datasets may miss co-occurring conditions | Per-cell independent classification |

### 15.4 Model Versioning & Auditability

Every analysis result stores the exact model version used. If a model is updated:
- Old results remain linked to old model version
- Rollback capability maintained for 6 months
- Model card published for each version (accuracy, training data, known limitations)

### 15.5 Human Oversight

The system is designed with **human-in-the-loop** principles:
- All positive results require explicit physician review
- Cell flagging system allows clinicians to override AI predictions
- Feedback mechanism: Clinicians can mark predictions as correct/incorrect
- Incorrect predictions collected (with consent) as training data for future versions

---

## 16. Project Roadmap & Milestones

### Phase 0: Foundation (Days 1–2)
- [ ] Repository setup, Docker Compose configured
- [ ] Database schema created and migrated
- [ ] MinIO buckets initialized
- [ ] FastAPI skeleton with health endpoint
- [ ] React app scaffold with design system tokens
- [ ] Authentication system (register/login/JWT)

### Phase 1: Core AI Pipeline (Days 3–5)
- [ ] YOLOv8 cell segmentation integrated
- [ ] Enhancement pipeline implemented and tested
- [ ] Malaria classifier training complete (baseline model)
- [ ] Malaria inference endpoint working end-to-end
- [ ] Basic results API returning mock + real data

### Phase 2: All Three Models (Days 6–8)
- [ ] Sickle cell classifier with shape feature fusion trained
- [ ] Thalassemia dual-head classifier trained
- [ ] All three classifiers integrated in parallel inference
- [ ] Grad-CAM heatmap generation working
- [ ] Smear-level aggregation report logic

### Phase 3: Full Backend (Days 9–11)
- [ ] Celery queue with Redis integration
- [ ] WebSocket progress broadcasts
- [ ] MinIO file storage fully integrated
- [ ] PDF report generation (ReportLab)
- [ ] Batch upload endpoint
- [ ] Rate limiting and security hardening

### Phase 4: Frontend (Days 12–15)
- [ ] Landing page
- [ ] Auth flows (login/register)
- [ ] Dashboard with stats
- [ ] Upload flow with drag-and-drop
- [ ] Analysis progress screen with WebSocket
- [ ] Results page with disease cards + confidence gauges
- [ ] Interactive cell map (fabric.js)
- [ ] Cell gallery with heatmaps
- [ ] History page

### Phase 5: Polish & Demo Prep (Days 16–18)
- [ ] End-to-end testing
- [ ] Load testing (Locust)
- [ ] Performance optimization (response caching, batch inference)
- [ ] Demo data: 5 sample smear images pre-analyzed
- [ ] One-click deploy script
- [ ] Documentation (README, API docs, model cards)
- [ ] Hackathon presentation deck

---

## 17. File & Folder Structure

```
hemavision/
├── README.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   │
│   └── app/
│       ├── main.py                    # FastAPI app factory
│       ├── config.py                  # Settings (pydantic-settings)
│       ├── celery_app.py              # Celery instance
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── dependencies.py        # Auth, DB session dependencies
│       │   └── v1/
│       │       ├── auth.py
│       │       ├── analysis.py
│       │       ├── batch.py
│       │       ├── admin.py
│       │       └── websocket.py
│       │
│       ├── models/                    # SQLAlchemy ORM models
│       │   ├── user.py
│       │   ├── job.py
│       │   ├── cell.py
│       │   └── model_version.py
│       │
│       ├── schemas/                   # Pydantic schemas
│       │   ├── auth.py
│       │   ├── analysis.py
│       │   ├── cell.py
│       │   └── report.py
│       │
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── storage_service.py     # MinIO operations
│       │   ├── report_service.py      # PDF generation
│       │   └── notification_service.py# WebSocket broadcasts
│       │
│       ├── tasks/
│       │   ├── analysis.py            # Main Celery task
│       │   └── cleanup.py             # Scheduled cleanup
│       │
│       └── ml/
│           ├── pipeline.py            # InferencePipeline class
│           ├── segmentor/
│           │   ├── yolov8_segmentor.py
│           │   └── sam_segmentor.py
│           ├── enhancement/
│           │   ├── pipeline.py
│           │   ├── stain_normalizer.py
│           │   └── cell_validator.py
│           ├── classifiers/
│           │   ├── base_classifier.py
│           │   ├── malaria_classifier.py
│           │   ├── sickle_classifier.py
│           │   └── thal_classifier.py
│           ├── explainability/
│           │   ├── gradcam.py
│           │   └── lime_explainer.py
│           └── aggregator.py          # Smear-level report aggregation
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css                  # Design tokens, global styles
│       │
│       ├── api/
│       │   ├── client.ts              # axios instance
│       │   ├── auth.ts
│       │   ├── analysis.ts
│       │   └── types.ts               # API response types
│       │
│       ├── store/
│       │   ├── useAppStore.ts         # Zustand store
│       │   └── useWebSocket.ts        # WS hook
│       │
│       ├── pages/
│       │   ├── Landing.tsx
│       │   ├── Auth.tsx
│       │   ├── Dashboard.tsx
│       │   ├── NewAnalysis.tsx
│       │   ├── AnalysisProcessing.tsx
│       │   ├── AnalysisResult.tsx
│       │   ├── History.tsx
│       │   ├── BatchUpload.tsx
│       │   └── Settings.tsx
│       │
│       ├── components/
│       │   ├── ui/                    # shadcn/ui components
│       │   ├── analysis/              # Analysis-specific components
│       │   ├── dashboard/             # Dashboard components
│       │   ├── layout/                # Layout components
│       │   └── common/                # Shared components
│       │
│       └── utils/
│           ├── formatters.ts
│           ├── validators.ts
│           └── imageUtils.ts
│
├── training/
│   ├── README.md
│   ├── requirements.txt
│   ├── configs/
│   │   ├── malaria_config.yaml
│   │   ├── sickle_config.yaml
│   │   └── thal_config.yaml
│   ├── datasets/
│   ├── models/
│   ├── trainers/
│   ├── evaluation/
│   ├── export/
│   └── train.py
│
├── models/                            # Production model weights (gitignored)
│   ├── segmentor/
│   ├── malaria/
│   ├── sickle/
│   └── thalassemia/
│
├── data/                              # Training data (gitignored)
│   ├── raw/
│   ├── processed/
│   └── splits/
│
├── nginx/
│   └── nginx.conf
│
├── scripts/
│   ├── setup.sh                       # First-run setup script
│   ├── download_models.sh             # Download pretrained weights
│   ├── download_datasets.sh           # Download training datasets
│   └── seed_demo_data.py              # Load demo analyses for judging
│
└── docs/
    ├── api.md                         # API reference
    ├── model_cards/
    │   ├── malaria_v3.2.md
    │   ├── sickle_v2.0.md
    │   └── thal_v1.5.md
    ├── architecture.md
    └── deployment.md
```

---

## 18. Environment Configuration

```bash
# .env.example
# ============================================
# HemaVision Environment Configuration
# ============================================

# Application
APP_NAME=HemaVision
ENVIRONMENT=development            # development | production
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=change-this-in-production

# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=hemavision
POSTGRES_USER=hemavision
POSTGRES_PASSWORD=change-this-password
DATABASE_URL=postgresql+asyncpg://hemavision:change-this-password@db:5432/hemavision

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=change-this-password
REDIS_URL=redis://:change-this-password@redis:6379

# MinIO / S3
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=change-this-password
MINIO_BUCKET=hemavision-storage
MINIO_SECURE=false                 # true in production with HTTPS

# JWT
JWT_SECRET=change-this-jwt-secret-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Model Configuration
MODEL_DIR=/app/models
SEGMENTOR_MODEL=yolov8n-blood-v2.1.pt
MALARIA_MODEL=efficientnet-b0-malaria-v3.2.pth
SICKLE_MODEL=mobilenetv3-sickle-v2.0.pth
THAL_MODEL=efficientnet-b2-thal-v1.5.pth
SEGMENTOR_TYPE=yolov8                # yolov8 | sam
DEVICE=cpu                           # cpu | cuda | mps

# Inference Settings
MIN_CELLS_FOR_ANALYSIS=50
MALARIA_POSITIVE_THRESHOLD=0.5
SICKLE_POSITIVE_THRESHOLD=0.05      # Smear-level: 5% of cells
THAL_POSITIVE_THRESHOLD=0.10        # Smear-level: 10% of cells
GRAD_CAM_MALARIA_THRESHOLD=0.7      # Generate heatmap if confidence > this
GRAD_CAM_SICKLE_THRESHOLD=0.8

# Storage Retention (days)
IMAGE_RETENTION_DAYS=90
CELL_CROP_RETENTION_DAYS=30
REPORT_RETENTION_DAYS=365

# Rate Limiting
RATE_LIMIT_GENERAL=60/minute
RATE_LIMIT_UPLOAD=10/hour
DAILY_ANALYSIS_QUOTA=50

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://hemavision.ai

# MLflow (development)
MLFLOW_TRACKING_URI=http://mlflow:5000

# Monitoring
SENTRY_DSN=                         # Optional
PROMETHEUS_ENABLED=true

# Frontend (Vite)
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 19. Third-Party Integrations

| Service | Purpose | Free Tier | Integration |
|---------|---------|-----------|-------------|
| Sentry | Error tracking, performance monitoring | 5K errors/month | `sentry-sdk[fastapi]` |
| SendGrid / Resend | Transactional email (account verification) | 100/day free | REST API |
| Cloudflare | CDN, DDoS protection | Generous free tier | DNS proxy |
| Prometheus + Grafana | Infrastructure monitoring | Self-hosted, free | prometheus-fastapi-instrumentator |
| MLflow | Experiment tracking | Self-hosted, free | mlflow Python SDK |
| GitHub Actions | CI/CD pipeline | Free for public repos | `.github/workflows/` |

### GitHub Actions CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
        working-directory: frontend
      - run: npm run test
        working-directory: frontend
      - run: npm run build
        working-directory: frontend

  model-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r training/requirements.txt
      - run: python training/evaluation/validate_models.py
        env:
          MODEL_DIR: ./models
```

---

## 20. Appendix: Prompt Engineering & Model Cards

### 20.1 Minimax 2.5 System Prompt for Blood Smear Analysis

The following prompt is designed for use with **Minimax 2.5** (or any frontier vision-language model) as a secondary validation layer or for generating natural-language clinical summaries of the ML model's output. This is NOT the primary detection model — it serves as a narrative synthesis and validation layer.

---

```
SYSTEM PROMPT — HEMAVISION CLINICAL SUMMARY GENERATOR (Minimax 2.5)

You are HemaVision-Clinical, a specialized biomedical AI assistant integrated into the HemaVision blood smear analysis platform. Your role is dual:

1. VISUAL VALIDATION: When provided with an annotated blood smear image and raw ML model outputs, validate the model's findings by examining the visual evidence and provide a calibrated second opinion.

2. CLINICAL NARRATIVE: Generate clear, structured clinical summaries of the automated analysis results that a medical professional can act upon.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT YOU WILL RECEIVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. The annotated blood smear image (with colored bounding boxes):
   - RED boxes = cells flagged positive for Malaria (ring-form parasites)
   - ORANGE boxes = cells flagged as sickle/abnormal shape (Sickle Cell)
   - YELLOW boxes = cells flagged as hypochromic/target (Thalassemia)
   - GREEN boxes = cells classified as normal

2. JSON report from the automated ML pipeline containing:
   - Total cells detected, RBC count
   - Disease predictions with confidence scores
   - Parasitemia rate, sickle rate, thalassemia abnormality rate
   - Cell type distributions

3. Optional: Individual high-confidence cell crops with Grad-CAM heatmaps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR VISUAL ANALYSIS PROTOCOL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When examining the smear image, specifically look for and comment on:

MALARIA INDICATORS:
- Presence of intraerythrocytic ring forms: small, pale circles with dark chromatin dot(s) inside RBCs
- Double infection (two rings per cell) — pathognomonic for P. falciparum
- Banana-shaped gametocytes — specific to P. falciparum
- Enlarged RBCs with Schuffner's dots — P. vivax or P. ovale
- Maurer's clefts — irregular inclusions in P. falciparum-infected cells
- Estimate percentage of cells showing parasites visually
- Note: ring forms are typically 1/5 to 1/3 the diameter of the host RBC

SICKLE CELL INDICATORS:
- Classic crescent or elongated banana-shaped RBCs
- Pointed ends (drepanocytes) vs blunt sickle forms
- Dense, dark-staining irreversibly sickled cells (ISCs)
- Target cells (central dense spot, pale ring, dense rim — "bulls-eye")
- Presence of normally shaped biconcave discs (percentage estimate)
- Degree of anisocytosis and poikilocytosis

THALASSEMIA/IDA INDICATORS:
- Central pallor: normal RBC has pallor <1/3 diameter; hypochromic >1/3
- Microcytosis: cells visually smaller than a lymphocyte nucleus (reference ~8µm)
- Target cells with classic bulls-eye appearance
- Pencil cells (cigar-shaped, elongated hypochromic cells)
- Basophilic stippling (fine purple granules distributed in cytoplasm)
- Anisocytosis: size variation across the field
- Poikilocytosis: shape variation beyond normal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate your response in the following structured format:

---
## Visual Examination Summary

### Image Quality Assessment
[Comment on staining quality, focus, cell distribution, cell density — flag any quality issues that may affect reliability]

### Malaria Assessment
**Visual Concordance with ML Model**: [Agree / Partially Agree / Disagree]
**Visual Findings**: [Describe what you observe in the image — ring forms, their characteristics, approximate distribution]
**Confidence**: [High / Moderate / Low] — [explain why]

### Sickle Cell Assessment  
**Visual Concordance with ML Model**: [Agree / Partially Agree / Disagree]
**Visual Findings**: [Describe cell shapes observed, sickle forms if any, target cells]
**Confidence**: [High / Moderate / Low]

### Thalassemia / Anemia Assessment
**Visual Concordance with ML Model**: [Agree / Partially Agree / Disagree]  
**Visual Findings**: [Central pallor, microcytosis, target cells, other features]
**Confidence**: [High / Moderate / Low]

---
## Integrated Clinical Summary

[2-3 sentences integrating findings from both the ML model and your visual examination. State primary finding, any secondary findings, and overall reliability of the analysis.]

## Clinical Recommendations

**Priority Level**: [URGENT / ROUTINE / MONITORING]

1. [Specific actionable recommendation]
2. [Confirmatory test recommendation if needed]
3. [Treatment pathway reference, citing WHO guidelines where applicable]

## Caveats & Limitations

[List any specific factors that reduce reliability of this analysis: poor staining, low cell count, unusual morphology, potential confounders]

---
⚠️ DISCLAIMER: This AI-assisted analysis is for screening purposes only. All findings must be reviewed and confirmed by a qualified medical professional before any clinical decision. This does not constitute a diagnosis.
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEHAVIORAL GUIDELINES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ACCURACY OVER CONFIDENCE: If you cannot clearly see ring forms in the image, say "Visual confirmation unclear at this resolution — ML model's assessment is primary." Do not fabricate visual observations.

2. CALIBRATED UNCERTAINTY: Use language that reflects your actual confidence. "Findings are consistent with..." vs "Definitively shows..." — be precise about what you can and cannot confirm visually.

3. CLINICAL LANGUAGE: Use proper medical terminology (trophozoites, schizogony, drepanocytes, hypochromia, microcytosis) but provide brief plain-language explanations for each technical term.

4. SEVERITY ALIGNMENT: Align your severity assessment with WHO standards:
   - Malaria parasitemia: <0.2% = low, 0.2-5% = moderate, >5% = severe, >10% = hyperparasitemia
   - Sickle cell: Report as percentage of sickled cells
   - Thalassemia: Note if pattern is consistent with trait (carrier) vs. major

5. NEVER DIAGNOSE: You assist, not diagnose. Always recommend physician confirmation and appropriate laboratory confirmation tests.

6. PEDIATRIC SENSITIVITY: If patient is identified as a child, note that reference ranges differ and flag for pediatric hematology specialist if findings are positive.

7. CO-OCCURRENCE: If findings suggest more than one condition, explicitly state this and note that complex presentations require specialist evaluation.
```

---

### 20.2 Model Cards

#### Model Card: Malaria Classifier v3.2

| Field | Value |
|-------|-------|
| Model Name | `efficientnet-b0-malaria-v3.2` |
| Architecture | EfficientNet-B0, fine-tuned |
| Task | Binary classification: Parasitized / Uninfected |
| Input | 64×64 RGB PNG, Macenko normalized |
| Output | Softmax probabilities over 2 classes |
| Training Dataset | NIH Malaria Cell Images (27,558 cells) |
| Training Split | 70/15/15 |
| Test Accuracy | 96.8% |
| Test Sensitivity | 96.1% |
| Test Specificity | 97.5% |
| Test AUC | 0.9847 |
| Parameters | 5.3M |
| Inference Time (CPU) | ~8ms per cell |
| Framework | PyTorch 2.2 |
| Known Limitations | May underperform on thick smears; ring forms < 1µm may be missed |

#### Model Card: Sickle Cell Classifier v2.0

| Field | Value |
|-------|-------|
| Model Name | `mobilenetv3-sickle-v2.0` |
| Architecture | MobileNetV3-Large + Shape Feature Fusion |
| Task | 4-class: Normal / Sickle / Target / Other |
| Input | 64×64 RGB + 12-dim shape features |
| Test Sickle F1 | 0.964 |
| Test Overall AUC | 0.983 |
| Parameters | 5.4M + shape head |
| Known Limitations | Sickle cells in non-crisis patients may appear nearly normal |

#### Model Card: Thalassemia Classifier v1.5

| Field | Value |
|-------|-------|
| Model Name | `efficientnet-b2-thal-v1.5` |
| Architecture | EfficientNet-B2, Dual-Head (Color + Morphology) |
| Task | 5-class: Normal / Hypochromic / Target / Pencil / Microcytic |
| Dataset | Chula RBC-12 (subset, 4 relevant classes) |
| Test Abnormal F1 | 0.891 |
| Test AUC | 0.937 |
| Parameters | 9.1M |
| Known Limitations | IDA vs Thalassemia distinction is challenging; both present similarly at cell level; confirmatory CBC + ferritin recommended |

---

*End of HemaVision Product Requirements Document*

*This document is version-controlled. Updates to model versions, API contracts, or deployment configuration should be reflected here with changelog entries.*

---

**Document Changelog**:
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | May 2026 | HemaVision Team | Initial PRD |
