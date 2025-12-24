# Insurance SaaS Platform - Backend

Python FastAPI backend for the Insurance Management SaaS Platform.

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Python**: 3.11+
- **Database**: PostgreSQL 15+, MongoDB 6+, Redis 7+
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT with OAuth2
- **Task Queue**: Celery with Redis

## Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- MongoDB 6+
- Redis 7+

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Application
APP_NAME=Insurance SaaS Platform
APP_VERSION=1.0.0
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/insurance_saas
MONGODB_URL=mongodb://localhost:27017/insurance_saas
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# File Storage
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### Database Setup

```bash
# Create PostgreSQL database
createdb insurance_saas

# Run migrations
alembic upgrade head

# Seed initial data
python -m app.scripts.seed_data
```

### Running the Application

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, access the auto-generated API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── alembic/                # Database migrations
│   ├── versions/
│   └── env.py
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/  # Route handlers
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── clients.py
│   │       │   └── companies.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   ├── security.py     # Auth utilities
│   │   └── dependencies.py # FastAPI dependencies
│   ├── models/             # SQLAlchemy models
│   │   ├── company.py
│   │   ├── user.py
│   │   ├── client.py
│   │   └── permission.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── client.py
│   │   └── company.py
│   ├── services/           # Business logic
│   │   ├── auth_service.py
│   │   ├── client_service.py
│   │   └── user_service.py
│   ├── repositories/       # Database access
│   │   ├── client_repository.py
│   │   └── user_repository.py
│   ├── utils/              # Helpers
│   │   └── helpers.py
│   └── main.py             # FastAPI app entry point
├── tests/
│   ├── test_auth.py
│   ├── test_clients.py
│   └── test_users.py
├── .env.example
├── requirements.txt
├── alembic.ini
└── README.md
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## License

Proprietary - Insurance SaaS Platform © 2025
