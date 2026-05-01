# ── Stage 1: deps ────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

# Copy package files from workspace root (npm workspaces)
COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/

# Install only production dependencies for the frontend workspace
RUN npm ci --workspace=tinsur-ai-frontend --omit=dev

# ── Stage 2: builder ─────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/frontend/node_modules ./frontend/node_modules 2>/dev/null || true

# Copy full source
COPY . .

# Build the Next.js app in standalone mode for minimal image size
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build --workspace=tinsur-ai-frontend

# ── Stage 3: runner ──────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser  --system --uid 1001 nextjs

# Standalone output (requires `output: 'standalone'` in next.config — see below)
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/static  ./frontend/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/frontend/public         ./frontend/public 2>/dev/null || true

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "frontend/server.js"]
