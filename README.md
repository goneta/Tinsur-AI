# Tinsur.AI - Intelligent Insurance Management System

Tinsur.AI is a modern, AI-powered insurance management platform featuring Policy Administration, Claims Processing with AI Damage Assessment, POS Management, and Accounting.

## Architecture
- **Backend**: FastAPI (Python), SQLAlchemy, PostgreSQL, LangChain/Gemini for AI Agents.
- **Frontend**: Next.js (TypeScript), Tailwind CSS, Shadcn/UI.
- **Database**: PostgreSQL (with PgVector for RAG).

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Google Gemini API Key

### Backend Setup
1.  Navigate to `backend`: `cd backend`
2.  Set up env: `cp .env.example .env` (Edit `.env` with your DB creds and API keys)
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run migrations: `alembic upgrade head`
5.  Seed data: `python -m app.scripts.seed_data`
6.  Start server: `uvicorn app.main:app --reload`

### Frontend Setup
1.  Navigate to `frontend`: `cd frontend`
2.  Install dependencies: `npm install`
3.  Start dev server: `npm run dev`

## Deployment
See `backend/README.md` and `frontend/README.md` for specific deployment details.
The system is Docker-ready (Dockerfiles included in respective directories).

## Features
- **POS Management**: Manage offices, agents, and inventory.
- **AI Agents**: Claims Assistant, Policy Helper, Telematics Analyzer.
- **Financials**: Automated Journal Entries, P&L, Balance Sheet.
- **Client Portal**: Self-service quotes and claims.
