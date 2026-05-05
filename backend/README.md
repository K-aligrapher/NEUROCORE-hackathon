# LokiVision Backend

FastAPI-based backend for blood smear analysis and disease detection.

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (local or Docker)
- Redis (local or Docker)
- MinIO (local or Docker) - for image storage

### Local Development Setup

#### 1. Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Setup Environment Variables
Create `.env` file in the backend directory:
```bash
cp .env.example .env  # if available, or create manually
```

Or edit `.env` with your database connection details:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/lokivision
REDIS_URL=redis://:password@localhost:6379
MINIO_ENDPOINT=localhost:9000
```

#### 4. Initialize Database
Create database tables:
```bash
python init_db.py
```

#### 5. Run Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000/api/v1`
API docs: `http://localhost:8000/docs`

---

## Docker Setup (Recommended)

Run all services with Docker Compose:

```bash
cd ..  # Go to project root
docker-compose up -d
```

This starts:
- **Backend API**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **MinIO**: `http://localhost:9001` (console)
- **Frontend**: `http://localhost:5173`

Check service health:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f api
```

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── analysis.py      # Image upload & analysis endpoints
│   │       └── auth.py          # Authentication endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py          # SQLAlchemy ORM models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── analysis.py          # Pydantic response schemas
│   ├── services/
│   │   ├── auth_service.py      # Auth logic
│   │   └── storage_service.py   # MinIO integration
│   ├── ml/
│   │   └── pipeline.py          # ML inference pipeline
│   ├── config.py                # Settings & configuration
│   ├── database.py              # SQLAlchemy setup
│   └── main.py                  # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (local)
├── Dockerfile                   # Docker configuration
└── init_db.py                   # Database initialization script
```

---

## API Endpoints

### Analysis
- **POST** `/api/v1/analysis/upload` - Upload image for analysis
- **GET** `/api/v1/analysis/{job_id}` - Get analysis results
- **GET** `/api/v1/analysis/history?limit=20` - Get analysis history

### Authentication
- **POST** `/api/v1/auth/register` - Register new user
- **POST** `/api/v1/auth/login` - Login user
- **POST** `/api/v1/auth/refresh` - Refresh access token

### Health
- **GET** `/api/v1/health` - Service health check

---

## Configuration

Key environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgres://user:pass@db:5432/lokivision |
| `REDIS_URL` | Redis connection string | redis://:pass@redis:6379 |
| `MINIO_ENDPOINT` | MinIO server address | minio:9000 |
| `JWT_SECRET` | JWT signing secret | lokivision-jwt-secret-... |
| `DEBUG` | Debug mode | True |
| `ENVIRONMENT` | Environment (development/production) | development |

---

## Troubleshooting

### Database Connection Error
```
Error: could not connect to server: Connection refused
```

**Solution**: Ensure PostgreSQL is running
```bash
# If using Docker
docker-compose up -d db

# If local, start PostgreSQL service
```

### Upload Fails - "No Images Found"
Ensure the `data/` directory exists and image files are readable.

### Models Not Found
Run the database initialization:
```bash
python init_db.py
```

### Port Already in Use
Change the port in the command:
```bash
uvicorn app.main:app --port 8001
```

---

## Development

### Run Tests
```bash
pytest tests/
```

### Format Code
```bash
black app/
isort app/
```

### Check Types
```bash
mypy app/
```

---

## Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Set secure `JWT_SECRET` and `SECRET_KEY`
3. Use production database and Redis instances
4. Configure proper CORS origins in `config.py`
5. Enable HTTPS
6. Use production ASGI server (Gunicorn + Uvicorn):

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
