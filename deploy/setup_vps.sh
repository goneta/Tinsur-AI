#!/usr/bin/env bash
#
# Tinsur-AI VPS bootstrap / repair script.
#
# Fixes the broken production state where:
#   - backend/venv is missing or was never created
#   - uvicorn is not installed ("No module named uvicorn")
#   - PM2 points at a uvicorn binary that does not exist
#   - tinsur-ai-backend processes are stopped / errored
#
# Run from anywhere on the VPS:
#   bash deploy/setup_vps.sh                 # backend venv + deps + PM2 restart
#   bash deploy/setup_vps.sh --migrate       # also run alembic upgrade head
#   bash deploy/setup_vps.sh --frontend      # also build + start the frontend
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
VENV_DIR="$BACKEND_DIR/venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

RUN_MIGRATIONS=0
WITH_FRONTEND=0
for arg in "$@"; do
  case "$arg" in
    --migrate)  RUN_MIGRATIONS=1 ;;
    --frontend) WITH_FRONTEND=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

echo "==> Repo root: $REPO_ROOT"

# ---------------------------------------------------------------- venv ----
if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "==> Creating virtualenv at $VENV_DIR"
  if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
    echo "ERROR: venv creation failed. On Debian/Ubuntu install it first:" >&2
    echo "  sudo apt-get install -y python3-venv" >&2
    exit 1
  fi
else
  echo "==> Virtualenv already exists at $VENV_DIR"
fi

echo "==> Installing backend dependencies (this can take several minutes)"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"

echo "==> Verifying critical imports"
"$VENV_DIR/bin/python" - <<'PY'
import fastapi, uvicorn, sqlalchemy
print(f"  fastapi    {fastapi.__version__}")
print(f"  uvicorn    {uvicorn.__version__}")
print(f"  sqlalchemy {sqlalchemy.__version__}")
PY

# ---------------------------------------------------------- migrations ----
if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "==> Running database migrations"
  (cd "$BACKEND_DIR" && "$VENV_DIR/bin/python" -m alembic upgrade head)
fi

# ------------------------------------------------------------ frontend ----
if [ "$WITH_FRONTEND" = "1" ]; then
  echo "==> Building frontend"
  (cd "$REPO_ROOT" && npm install && npm run build)
fi

# ----------------------------------------------------------------- PM2 ----
if ! command -v pm2 >/dev/null 2>&1; then
  echo "ERROR: pm2 is not installed. Install it with: npm install -g pm2" >&2
  exit 1
fi

mkdir -p "$BACKEND_DIR/logs" "$REPO_ROOT/frontend/logs"

echo "==> Restarting PM2 processes from ecosystem.config.js"
pm2 delete tinsur-ai-backend >/dev/null 2>&1 || true
pm2 start "$REPO_ROOT/ecosystem.config.js" --only tinsur-ai-backend

if [ "$WITH_FRONTEND" = "1" ]; then
  pm2 delete tinsur-ai-frontend >/dev/null 2>&1 || true
  pm2 start "$REPO_ROOT/ecosystem.config.js" --only tinsur-ai-frontend
fi

pm2 save

echo "==> Done. Current PM2 status:"
pm2 status

echo ""
echo "Health check: curl -s http://127.0.0.1:8000/health"
