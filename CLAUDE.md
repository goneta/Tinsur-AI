# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Tinsur-AI is a multi-tenant insurance management SaaS platform:

- **Backend** — FastAPI + SQLAlchemy + Alembic in `backend/` (entrypoint `backend/app/main.py`, port 8000). AI/A2A agents live in `backend/agents/`. `backend/libs/` is vendored dependency code — do not edit it.
- **Frontend** — Next.js App Router in `frontend/` (npm workspace `tinsur-ai-frontend`, port 3000). A legacy root-level `app/` + `components/` + `lib/` tree also exists; check which tree a page belongs to before editing.

## DOX documentation contract

This repo uses the DOX framework (see root `AGENTS.md`):

- `AGENTS.md` files are binding contracts for their subtrees. Before editing, read the root `AGENTS.md` plus every `AGENTS.md` on the path to each file you touch. After any meaningful change, do a DOX pass and update the nearest owning `AGENTS.md`.
- Important source files under `backend/`, `frontend/`, root `app/`, root `components/`, and root `lib/` have sibling docs named `<filename>.md` (e.g. `main.py.md`). Keep them current when behavior, side effects, or dependencies change.

## Development commands

```bash
# Frontend (from repo root, npm workspaces)
npm run dev        # next dev
npm run build      # next build
npm run start      # next start

# Backend (from backend/)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
python -m pytest                 # backend tests
python -m alembic upgrade head   # migrations
```

## Production deployment (VPS + PM2)

Production runs on a Linux VPS under PM2, defined in the root `ecosystem.config.js`:

- `tinsur-ai-backend` — `backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `tinsur-ai-frontend` — `next start` on port 3000 (needs `npm run build` first)

**The backend must always run through the virtualenv at `backend/venv` — never a bare/global `uvicorn`.** To bootstrap or repair the server (missing venv, `No module named uvicorn`, errored PM2 processes):

```bash
bash deploy/setup_vps.sh              # venv + deps + PM2 restart
bash deploy/setup_vps.sh --migrate    # also run alembic migrations
bash deploy/setup_vps.sh --frontend   # also build + start the frontend
```

Full runbook: `TINSUR_AI_PRODUCTION_DEPLOYMENT_GUIDE.md` → "Option 4: PM2 Deployment (VPS)".

## Git workflow

- All development happens on the **`main`** branch; keep `main` up to date with any commits landing on `master`.
- Remote: https://github.com/goneta/Tinsur-AI.git
- Shell scripts keep LF line endings (enforced via `.gitattributes`) so they run on the Linux VPS.
