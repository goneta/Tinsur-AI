# Tinsur-AI v1.0.0 Production Deployment Guide

**Version:** 1.0.0  
**Date:** 2026-03-25  
**Status:** Ready for Deployment  
**Audience:** DevOps, Site Reliability Engineers  

---

## TABLE OF CONTENTS

1. [Pre-Deployment](#pre-deployment)
2. [Deployment Steps](#deployment-steps)
3. [Post-Deployment Verification](#post-deployment-verification)
4. [Monitoring & Alerting](#monitoring--alerting)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)

---

## PRE-DEPLOYMENT

### Requirements Checklist

#### Infrastructure
- [ ] PostgreSQL 14+ instance (or compatible)
- [ ] At least 2GB RAM available
- [ ] At least 10GB disk space
- [ ] Network connectivity to required services
- [ ] SSL/TLS certificates obtained
- [ ] Load balancer configured (optional)
- [ ] CDN configured (optional)

#### External Services
- [ ] Sentry account created (or error tracking alternative)
- [ ] Monitoring dashboard configured (DataDog, New Relic, etc.)
- [ ] Log aggregation service (optional but recommended)
- [ ] Backup storage configured (S3, GCS, etc.)

#### Credentials & Secrets
- [ ] PostgreSQL credentials secured
- [ ] Sentry DSN obtained
- [ ] API keys generated
- [ ] Secrets stored in secure vault (HashiCorp Vault, AWS Secrets Manager, etc.)
- [ ] SSL certificates prepared

#### Documentation
- [ ] Team trained on deployment procedure
- [ ] Incident response plan reviewed
- [ ] Escalation procedures defined
- [ ] On-call rotation established
- [ ] Runbook prepared

### Environment Setup

```bash
# 1. Create production environment file
cat > .env.production << EOF
# Application
APP_NAME=Tinsur.AI
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@prod-db.example.com:5432/tinsur_ai

# Security
SECRET_KEY=$(openssl rand -hex 32)
A2A_INTERNAL_API_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Error Tracking
SENTRY_DSN=https://key@sentry.io/project_id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# CORS Origins
ALLOWED_ORIGINS=https://tinsur.example.com,https://admin.tinsur.example.com

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/tinsur-ai/app.log

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Additional APIs
GOOGLE_API_KEY=${GOOGLE_API_KEY_PROD}
FACEBOOK_APP_ID=${FACEBOOK_APP_ID_PROD}
EOF

# 2. Verify configuration
python verify_production_readiness.py

# 3. If all checks pass, proceed to deployment
```

---

## DEPLOYMENT STEPS

### Option 1: Docker Deployment (Recommended)

```bash
# Step 1: Build container
docker build \
  -t tinsur-ai:1.0.0 \
  -f backend/Dockerfile \
  .

# Step 2: Tag for registry
docker tag tinsur-ai:1.0.0 your-registry/tinsur-ai:1.0.0

# Step 3: Push to registry
docker push your-registry/tinsur-ai:1.0.0

# Step 4: Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/tinsur-ai-deployment.yaml
kubectl apply -f k8s/tinsur-ai-service.yaml

# Step 5: Verify deployment
kubectl get deployments -n tinsur-ai
kubectl get pods -n tinsur-ai
kubectl logs -n tinsur-ai deployment/tinsur-ai
```

### Option 2: Direct Python Deployment

```bash
# Step 1: Install dependencies
cd backend
pip install -r requirements.txt

# Step 2: Initialize database
python -m alembic upgrade head

# Step 3: Seed initial data (if needed)
python scripts/seed_data.py

# Step 4: Start application
python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-config logging_production.yaml \
  --access-log \
  --use-colors

# Step 5: Monitor
tail -f /var/log/tinsur-ai/app.log
```

### Option 3: Systemd Service (Linux)

```bash
# Step 1: Create service file
sudo tee /etc/systemd/system/tinsur-ai.service << EOF
[Unit]
Description=Tinsur-AI Insurance SaaS Platform
After=network.target

[Service]
Type=notify
User=tinsur
WorkingDirectory=/opt/tinsur-ai
Environment="PATH=/opt/tinsur-ai/venv/bin"
ExecStart=/opt/tinsur-ai/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 2: Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tinsur-ai
sudo systemctl start tinsur-ai

# Step 3: Check status
sudo systemctl status tinsur-ai
```

---

## POST-DEPLOYMENT VERIFICATION

### Immediate Checks (First 5 minutes)

```bash
# 1. Health endpoint
curl https://api.tinsur.example.com/health
# Expected: {"status": "healthy", "version": "1.0.0"}

# 2. Swagger documentation
curl https://api.tinsur.example.com/docs
# Expected: HTTP 200, Swagger UI loads

# 3. OpenAPI schema
curl https://api.tinsur.example.com/openapi.json
# Expected: HTTP 200, complete schema

# 4. Check logs
tail -f /var/log/tinsur-ai/app.log
# Expected: No ERROR or CRITICAL messages

# 5. Verify database connection
curl -X GET https://api.tinsur.example.com/api/v1/health/db
# Expected: Database connected
```

### Smoke Tests (First 15 minutes)

```bash
# 1. Test quote endpoint
curl -X POST https://api.tinsur.example.com/api/v1/quotes/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_type": "auto",
    "coverage_amount": 100000,
    "duration_months": 12
  }'

# 2. Test agent endpoint
curl -X POST https://api.tinsur.example.com/api/v1/agents/quote \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "Calculate premium for 35-year-old driver"}'

# 3. Test error handling
curl -X POST https://api.tinsur.example.com/api/v1/quotes/calculate \
  -H "Content-Type: application/json" \
  -d '{}'
# Expected: HTTP 422 with validation error

# 4. Test rate limiting
for i in {1..150}; do
  curl -s https://api.tinsur.example.com/api/v1/health
done | grep "429"
# Expected: Some 429 responses after 100 requests
```

### Full Validation (First hour)

```bash
# 1. Run complete test suite
pytest tests/ -v --cov=app --cov-report=html

# 2. Check all endpoints respond
python verify_production_readiness.py

# 3. Complete Phase 1 quote parity tests
python test_quote_parity.py

# 4. Verify monitoring is capturing data
# Check Sentry dashboard for captured events
# Check metrics in DataDog/New Relic
# Verify logs in ELK/Splunk

# 5. Performance baseline
# Record CPU usage, memory, response times
# Document these as baseline for future comparisons
```

---

## MONITORING & ALERTING

### Metric Collection

#### Application Metrics
```
- api_request_count (total requests)
- api_response_time (latency distribution)
- api_error_rate (5xx errors / total)
- active_requests (concurrent requests)
```

#### Business Metrics
```
- quotes_created (daily)
- policies_issued (daily)
- claims_filed (daily)
- agent_success_rate (%)
```

#### Infrastructure Metrics
```
- cpu_usage (%)
- memory_usage (%)
- disk_usage (%)
- network_io (Mbps)
- database_connections (count)
```

### Alert Thresholds

#### Critical (Page immediately)
- Error rate > 1%
- Response time (p99) > 5 seconds
- Database connection pool exhausted
- Disk usage > 90%
- API downtime > 1 minute

#### Warning (Alert but don't page)
- Error rate > 0.5%
- Response time (p95) > 1 second
- Memory usage > 80%
- Disk usage > 75%
- Agent success rate < 90%

#### Info (Log for review)
- Slow queries (> 1 second)
- Agent response time > 3 seconds
- Cache hit rate < 70%
- New security events

### Dashboard Configuration

Create dashboards for:
1. **Operations** - Overall health, errors, performance
2. **Business** - Quotes, policies, revenue
3. **Infrastructure** - CPU, memory, disk, network
4. **Security** - Auth attempts, blocked requests, suspicious activity

---

## TROUBLESHOOTING

### Application Won't Start

```bash
# 1. Check configuration
python -m app.core.config_production
# Should show all required env vars

# 2. Test database connection
python -c "from app.core.database import engine; engine.connect()"
# Should connect successfully

# 3. Check logs
tail -f /var/log/tinsur-ai/app.log

# 4. Verify dependencies
pip install -r requirements.txt --force-reinstall

# 5. Test in debug mode (temporary only)
DEBUG=True python -m uvicorn app.main:app
```

### High Error Rate

```bash
# 1. Check error logs
grep ERROR /var/log/tinsur-ai/error.log | tail -20

# 2. Check Sentry
# Review recent issues in Sentry dashboard

# 3. Check database
# Verify database is accessible and responsive

# 4. Check external APIs
# Verify Gemini API is accessible
# Check API rate limits

# 5. Scale if needed
# Increase worker processes
# Add more database connections
```

### Slow Response Times

```bash
# 1. Check database query times
# Enable query logging
SET log_statement='all';

# 2. Review slow query log
# Find N+1 queries
# Optimize database indexes

# 3. Check external API calls
# Verify Gemini API response times
# Check network latency

# 4. Profile application
# Use py-spy for CPU profiling
# Use memory_profiler for memory issues

# 5. Scale infrastructure
# Add more CPU
# Add more memory
# Enable caching
```

### Database Issues

```bash
# 1. Connection pool exhausted
# Increase pool size in .env
# Review long-running queries

# 2. Disk space low
# Backup and archive old data
# Increase disk size

# 3. Performance degradation
# Analyze query plans
# Add indexes where needed
# Partition large tables

# 4. Replication lag
# Verify network connectivity
# Check replica performance
# Increase replication batch size
```

---

## ROLLBACK PROCEDURES

### Quick Rollback (< 5 minutes)

```bash
# 1. Stop new deployment
kubectl rollout undo deployment/tinsur-ai -n tinsur-ai
# or
systemctl restart tinsur-ai --rollback

# 2. Verify previous version
curl https://api.tinsur.example.com/health

# 3. Monitor
tail -f /var/log/tinsur-ai/app.log
```

### Full Rollback (< 30 minutes)

```bash
# 1. Stop current deployment
kubectl scale deployment tinsur-ai --replicas=0 -n tinsur-ai

# 2. Restore database backup (if schema changed)
pg_restore -d tinsur_ai backup.sql.gz

# 3. Deploy previous version
docker pull your-registry/tinsur-ai:1.0.0-previous
kubectl set image deployment/tinsur-ai \
  tinsur-ai=your-registry/tinsur-ai:1.0.0-previous -n tinsur-ai

# 4. Verify deployment
kubectl get pods -n tinsur-ai
curl https://api.tinsur.example.com/health
```

### Data Recovery

```bash
# If data corruption suspected
# 1. Stop application
# 2. Restore database from backup
pg_restore -d tinsur_ai backup-clean.sql.gz

# 3. Validate data
python scripts/validate_data.py

# 4. Restart application
systemctl start tinsur-ai
```

---

## PRODUCTION RUNBOOK CHECKLIST

### Before Deployment
- [ ] All prerequisites met
- [ ] Team trained
- [ ] Rollback plan reviewed
- [ ] Monitoring configured
- [ ] Backups tested
- [ ] Communication plan ready

### During Deployment
- [ ] Change ticket created
- [ ] Team alerted
- [ ] Deployment window opened
- [ ] Steps executed carefully
- [ ] Monitoring watched closely
- [ ] Issues escalated immediately

### After Deployment
- [ ] Health checks passed
- [ ] Error rate normal
- [ ] Performance acceptable
- [ ] Team debriefed
- [ ] Documentation updated
- [ ] Metrics baseline recorded

---

## SUPPORT CONTACTS

**Technical Lead:** _______________  
**Security Officer:** _______________  
**Operations Lead:** _______________  
**On-Call:** _______________  

**Escalation Path:** Team Lead → Manager → Director

---

## FINAL NOTES

- Deployment should take 30-45 minutes for full stabilization
- Monitor closely for first 24 hours
- Be prepared to rollback if issues arise
- Document any incidents for post-mortem
- Update runbook based on lessons learned

**Questions?** Contact the technical lead or on-call team.
