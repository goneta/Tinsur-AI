# Tinsur-AI Administrator Onboarding Guide v1.0.0

**Welcome to Tinsur-AI** — Administrator Setup Guide

---

## For System Administrators

This guide covers system setup, user management, and configuration for Tinsur-AI administrators.

### Admin Responsibilities

- **User Management** — Create, edit, deactivate accounts
- **Role & Permissions** — Configure access control
- **Organization Settings** — Manage company profile
- **Integrations** — Set up connections to external systems
- **Compliance** — Ensure regulatory compliance
- **Security** — Manage security settings and 2FA
- **Reporting** — Monitor system health and usage
- **Support** — Escalate issues and manage support tickets

### Initial Setup Checklist

- [ ] Create administrator account
- [ ] Complete organization profile
- [ ] Configure logo and branding
- [ ] Set up team members with appropriate roles
- [ ] Enable security features (2FA, password policies)
- [ ] Configure integrations (if applicable)
- [ ] Set up backup and disaster recovery
- [ ] Review compliance requirements
- [ ] Schedule staff training

### User Management

#### Create a New User

1. Go to **Settings** → **Team Management**
2. Click **"+ Add User"**
3. Enter:
   - Full Name
   - Email Address
   - Role (Admin, Manager, Agent, Viewer, Custom)
4. Click **"Send Invitation"**
5. User receives email with setup link

#### Configure Roles

- **Administrator** — Full system access, manage users
- **Manager** — Create clients, approve quotes, manage team
- **Agent** — Create clients, generate quotes (own clients only)
- **Viewer** — Read-only access to reports
- **Custom** — Create custom permission sets

#### Deactivate Users

When team member leaves:
1. Go to **Settings** → **Team Management**
2. Find user and click **"Deactivate"**
3. Confirm action
4. User loses all access immediately

### Security Configuration

#### Password Policies

1. Go to **Settings** → **Security**
2. Set password requirements:
   - Minimum length (recommend 12+ characters)
   - Complexity rules (uppercase, numbers, symbols)
   - Expiration period (recommend 90 days)
   - History (prevent password reuse)

#### Two-Factor Authentication (2FA)

1. Go to **Settings** → **Security** → **2FA**
2. Enable 2FA globally or per-role
3. Require all admins use 2FA
4. Provide users with authenticator app options (Google Authenticator, Microsoft Authenticator, etc.)

#### Login Security

1. Configure IP whitelisting (enterprise feature)
2. Set session timeout (recommend 15 minutes)
3. Enable login notifications
4. Monitor failed login attempts

### Integration Setup

#### Connect External Systems

1. Go to **Settings** → **Integrations**
2. Select system to integrate (CRM, Accounting, Email, etc.)
3. Authorize access using OAuth or API key
4. Test connection
5. Configure sync frequency

**Supported Integrations:**
- QuickBooks, Xero (Accounting)
- Salesforce, HubSpot (CRM)
- Google Workspace, Microsoft 365 (Email/Calendar)
- Custom API integrations

### Compliance Management

#### GDPR Compliance

1. Document data processing agreement (DPA)
2. Configure data retention periods
3. Set up right-to-deletion workflow
4. Monitor data access logs
5. Train staff on data handling

#### Audit Logging

1. Go to **Settings** → **Activity Log**
2. Review system events:
   - User logins
   - Data modifications
   - Configuration changes
   - Exports and reports
3. Export audit logs for compliance

### Backup & Disaster Recovery

1. Go to **Settings** → **Backup**
2. Verify daily backup schedule
3. Test restore procedures quarterly
4. Document recovery procedures
5. Communicate disaster recovery plan to team

### Monitoring & Health

#### System Health Dashboard

1. Go to **Settings** → **System Health**
2. Monitor:
   - Server status
   - Database performance
   - API response times
   - Storage usage
   - Backup status

#### Usage Analytics

1. Go to **Reports** → **Admin Reports**
2. Track:
   - Active users
   - Data volume
   - Feature usage
   - Performance metrics

### Support & Documentation

- **Admin Support:** admin-support@tinsur-ai.com
- **Documentation:** docs.tinsur-ai.com/admin
- **Training:** admin-training@tinsur-ai.com
- **Emergency Support:** +44 (0) 20 XXXX XXXX

---

**Version:** 1.0.0  
**Last Updated:** March 2026

© 2026 Tinsur-AI. All rights reserved.
