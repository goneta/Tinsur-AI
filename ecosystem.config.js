/**
 * PM2 process configuration for the Tinsur-AI VPS deployment.
 *
 * The backend MUST run through the project virtualenv at backend/venv —
 * never through a bare `uvicorn` command. If the venv does not exist yet,
 * run `bash deploy/setup_vps.sh` first; it creates the venv, installs
 * backend/requirements.txt, and (re)starts these processes.
 *
 * Usage on the VPS (from the repository root):
 *   pm2 start ecosystem.config.js            # start backend + frontend
 *   pm2 start ecosystem.config.js --only tinsur-ai-backend
 *   pm2 save                                  # persist across reboots
 */
module.exports = {
  apps: [
    {
      name: 'tinsur-ai-backend',
      cwd: './backend',
      // Run uvicorn via the venv interpreter so PM2 never depends on a
      // globally installed uvicorn binary.
      script: './venv/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000',
      interpreter: 'none',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      kill_timeout: 10000,
      env: {
        PYTHONUNBUFFERED: '1',
        ENVIRONMENT: 'production',
      },
      out_file: './logs/pm2-backend-out.log',
      error_file: './logs/pm2-backend-error.log',
      merge_logs: true,
      time: true,
    },
    {
      name: 'tinsur-ai-frontend',
      cwd: './frontend',
      // Requires a prior production build: npm run build (from repo root or frontend/)
      script: 'npm',
      args: 'run start',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        NODE_ENV: 'production',
        PORT: '3000',
      },
      out_file: './logs/pm2-frontend-out.log',
      error_file: './logs/pm2-frontend-error.log',
      merge_logs: true,
      time: true,
    },
  ],
};
