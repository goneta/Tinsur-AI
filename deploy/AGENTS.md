# DOX framework

## Purpose

- Owns VPS deployment tooling: server bootstrap/repair scripts used together with the root `ecosystem.config.js` PM2 configuration.

## Ownership

- `setup_vps.sh` - creates/repairs `backend/venv`, installs `backend/requirements.txt`, optionally runs Alembic migrations and the frontend build, then (re)starts the PM2 processes and saves the process list.
- The PM2 process definition itself lives at the repository root in `ecosystem.config.js` (root-owned); this folder owns how it gets bootstrapped on a server.

## Local Contracts

- The backend must always be started through the project virtualenv (`backend/venv/bin/python -m uvicorn app.main:app`); never rely on a globally installed `uvicorn` binary.
- Scripts in this folder run on the Linux VPS and must keep LF line endings (enforced by `.gitattributes`).
- PM2 process names are `tinsur-ai-backend` (port 8000) and `tinsur-ai-frontend` (port 3000); keep names stable because operators reference them in `pm2 restart` commands.

## Work Guidance

- Full VPS runbook: `TINSUR_AI_PRODUCTION_DEPLOYMENT_GUIDE.md` → "Option 4: PM2 Deployment (VPS)".

## Verification

- On the VPS: `bash deploy/setup_vps.sh` completes without error, `pm2 status` shows both processes `online`, and `curl http://127.0.0.1:8000/health` returns a healthy response.

## Child DOX Index

- None.
