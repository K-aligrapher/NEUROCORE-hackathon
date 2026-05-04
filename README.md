# LokiVision
## Blood Smear Analysis & Disease Detection System

AI-powered blood smear analysis platform for detecting Malaria, Sickle Cell Anemia, and Thalassemia.

## Quick Start

```bash
# Clone and setup
cp .env.example .env
docker-compose up -d

# Access
# Frontend: http://localhost:5173
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Features

- **Malaria Detection** - Identifies parasitized RBCs (ring forms)
- **Sickle Cell Analysis** - Detects sickle-shaped cells
- **Thalassemia Screening** - Identifies hypochromic/target cells
- **Real-time Progress** - WebSocket updates
- **Interactive Results** - Cell-level analysis with heatmaps

## Tech Stack

- **Backend**: FastAPI, Celery, PostgreSQL, Redis, MinIO
- **Frontend**: React 18, TypeScript, Tailwind CSS, shadcn/ui
- **ML**: PyTorch, YOLOv8, OpenCV