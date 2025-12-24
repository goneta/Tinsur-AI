# AI Task Planning Template - Phase 1: Foundation Setup

> **About This Task:** This task covers the foundational setup for the Insurance SaaS Platform, establishing the core architecture, authentication system, and basic client management capabilities.

---

## 1. Task Overview

### Task Title
**Title:** Phase 1: Foundation Setup - Core System, Authentication & Multi-Tenancy

### Goal Statement
**Goal:** Establish the foundational architecture for the Insurance SaaS Platform with Python FastAPI backend, Next.js frontend, multi-tenant database architecture, secure authentication system, and basic client management. This phase creates the technical foundation that all subsequent features will build upon.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Backend Framework**: Python FastAPI 0.104+
- **Frontend Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (Frontend), Python 3.11+ (Backend)
- **Database & ORM**: PostgreSQL 15+ (primary), MongoDB 6+ (documents), SQLAlchemy 2.0+ (ORM), Redis 7+ (cache)
- **UI & Styling**: shadcn/ui with Radix UI components, Tailwind CSS
- **Authentication**: JWT with OAuth2, bcrypt for password hashing
- **Key Architectural Patterns**: Multi-tenant SaaS, Microservices-ready monolith, Repository pattern, API-first design

### Current State
This is a **greenfield project** starting from scratch. No existing codebase. We need to establish:
- Complete development environment
- Project structure for both backend and frontend
- Database schemas with multi-tenancy support
- API framework with automatic documentation
- Authentication and authorization infrastructure
- Basic admin and client interfaces

## 3. Context & Problem Definition

### Problem Statement
Insurance companies in Côte d'Ivoire lack modern, integrated digital platforms to manage their operations. They need a secure, scalable SaaS solution that can handle multi-tenant scenarios, provide role-based access control, manage client data, and establish a foundation for advanced features like AI assistance and payment processing. This phase must create a rock-solid foundation that supports 99.9% uptime and horizontal scalability.

### Success Criteria
- [x] Backend API successfully running with FastAPI
- [x] Frontend Next.js application successfully running
- [x] PostgreSQL and MongoDB databases connected and operational
- [x] Multi-tenant architecture implemented with data isolation
- [x] User authentication working (login, logout, token refresh)
- [x] RBAC system functioning with at least 4 roles (Super Admin, Company Admin, Agent, Client)
- [x] Client registration and profile management operational
- [x] Document upload system working with cloud storage
- [x] Admin dashboard displaying system metrics
- [x] API documentation auto-generated and accessible

---

## 4. Development Mode Context

### Development Mode Context
- **🚨 Project Stage:** New development - greenfield project with no legacy constraints
- **Breaking Changes:** Acceptable - establish best practices from the start
- **Data Handling:** No existing data to preserve
- **User Base:** Development team only during this phase
- **Priority:** Balanced - strong foundation is critical, but stay on 4-month timeline

---

## 5. Technical Requirements

### Functional Requirements

**User Authentication:**
- User can register with email and password
- User can login and receive JWT access token
- User can refresh token before expiration
- User can logout and invalidate token
- System automatically enforces password complexity rules
- System supports multi-factor authentication (MFA) setup

**Role-Based Access Control:**
- System assigns roles: Super Admin, Company Admin, Manager, Agent, Client
- System enforces permissions based on assigned role
- User can only access features permitted by their role
- Admin can create custom roles with specific permissions
- System logs all permission checks for audit

**Client Management:**
- User (Agent/Admin) can create new client profiles
- User can update client information (personal, contact, beneficiaries)
- User can view list of all clients with pagination and search
- User can upload client documents (ID, driver's license, etc.)
- System automatically stores documents in cloud storage
- System tracks all client interactions and modifications

**Multi-Tenancy:**
- System isolates data between insurance companies
- Each company has unique subdomain or company identifier
- Company admin can customize company profile and branding
- System prevents cross-company data access
- System supports company-specific feature toggles

**Admin Dashboard:**
- Admin can view total number of users by role
- Admin can view total number of clients
- Admin can view recent registrations
- Admin can view system health metrics
- Admin can access API documentation

### Non-Functional Requirements
- **Performance:** API response time < 500ms for 95th percentile
- **Security:** All passwords hashed with bcrypt, JWT tokens with 15-min expiry, HTTPS only
- **Usability:** Intuitive UI following modern SaaS design patterns, accessible (WCAG 2.1 AA)
- **Responsive Design:** Fully functional on mobile (375px), tablet (768px), desktop (1920px)
- **Theme Support:** Light mode only in Phase 1 (using dashboard_visual_description.md design)

### Technical Constraints
- Must use Python FastAPI for backend (per project requirements)
- Must use Next.js 14+ for frontend (per project requirements)
- Must support multi-tenancy from day one
- Must use PostgreSQL as primary database
- Must follow design system from dashboard_visual_description.md

---

## 6. Data & Database Changes

### Database Schema Changes

**PostgreSQL Tables:**

```sql
-- Companies table (multi-tenancy)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    features JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    role VARCHAR(50) NOT NULL, -- 'super_admin', 'company_admin', 'manager', 'agent', 'client'
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(email, company_id)
);

-- Clients table
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    client_type VARCHAR(50) NOT NULL, -- 'individual', 'corporate'
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    business_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    id_number VARCHAR(100),
    tax_id VARCHAR(100),
    risk_profile VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'inactive', 'suspended'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Permissions table
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(100) NOT NULL, -- 'clients', 'policies', 'claims', etc.
    action VARCHAR(50) NOT NULL, -- 'create', 'read', 'update', 'delete'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Role_permissions table
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role VARCHAR(50) NOT NULL,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(role, permission_id)
);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    resource_id UUID,
    changes JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_clients_company_id ON clients(company_id);
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_audit_logs_company_id ON audit_logs(company_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

**MongoDB Collections:**

```javascript
// documents collection
{
  _id: ObjectId,
  company_id: UUID,
  client_id: UUID,
  document_type: String, // 'id_card', 'driver_license', 'vehicle_registration', etc.
  file_name: String,
  file_url: String,
  file_size: Number,
  mime_type: String,
  uploaded_by: UUID,
  uploaded_at: Date,
  metadata: {
    extracted_data: Object, // OCR results (Phase 3)
    verified: Boolean,
    verified_by: UUID,
    verified_at: Date
  },
  created_at: Date,
  updated_at: Date
}
```

### Data Model Updates

**TypeScript Interfaces (Frontend):**

```typescript
// User types
interface User {
  id: string;
  company_id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: 'super_admin' | 'company_admin' | 'manager' | 'agent' | 'client';
  is_active: boolean;
  is_verified: boolean;
  mfa_enabled: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

// Client types
interface Client {
  id: string;
  company_id: string;
  user_id?: string;
  client_type: 'individual' | 'corporate';
  first_name?: string;
  last_name?: string;
  business_name?: string;
  email: string;
  phone: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  city?: string;
  country: string;
  id_number?: string;
  tax_id?: string;
  risk_profile: 'low' | 'medium' | 'high';
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  updated_at: string;
}

// Auth types
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}
```

**Python Models (Backend):**

```python
# SQLAlchemy models in backend/models/

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    features = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="company")
    clients = relationship("Client", back_populates="company")

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = relationship("Company", back_populates="users")
```

### Data Migration Plan

1. **Initial Setup:**
   - Create PostgreSQL database
   - Create MongoDB database
   - Run Alembic migrations for PostgreSQL tables
   - Create MongoDB indexes

2. **Seed Data:**
   - Create default permissions for all roles
   - Create super admin user
   - Create demo company for testing

3. **Validation:**
   - Verify all tables created successfully
   - Verify foreign key constraints
   - Verify indexes created
   - Test multi-tenant data isolation

---

## 7. API & Backend Changes

### Data Access Pattern Rules

**Backend Structure:**
- `backend/models/` - SQLAlchemy ORM models
- `backend/schemas/` - Pydantic schemas for validation
- `backend/routers/` - FastAPI route handlers
- `backend/services/` - Business logic layer
- `backend/repositories/` - Database access layer
- `backend/core/` - Configuration, security, dependencies
- `backend/utils/` - Helper functions

**Pattern:**
- Use repository pattern for database operations
- Business logic in service layer
- Route handlers are thin, delegate to services
- Dependency injection for database sessions

### Server Actions

**Authentication Endpoints (`/api/v1/auth`):**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and invalidate tokens
- `POST /auth/verify-email` - Verify email address
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

**User Endpoints (`/api/v1/users`):**
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users` - List users (admin only)
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Deactivate user

**Client Endpoints (`/api/v1/clients`):**
- `POST /clients` - Create new client
- `GET /clients` - List clients with pagination and filters
- `GET /clients/{id}` - Get client by ID
- `PUT /clients/{id}` - Update client
- `DELETE /clients/{id}` - Delete client
- `POST /clients/{id}/documents` - Upload document for client
- `GET /clients/{id}/documents` - Get client documents

**Company Endpoints (`/api/v1/companies`):**
- `GET /companies/me` - Get current company
- `PUT /companies/me` - Update company profile
- `GET /companies` - List all companies (super admin only)

### Database Queries

Use SQLAlchemy with repository pattern. Example:

```python
# backend/repositories/client_repository.py
class ClientRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, client_id: UUID, company_id: UUID) -> Optional[Client]:
        return self.db.query(Client).filter(
            Client.id == client_id,
            Client.company_id == company_id
        ).first()
    
    def get_all(self, company_id: UUID, skip: int = 0, limit: int = 100) -> List[Client]:
        return self.db.query(Client).filter(
            Client.company_id == company_id
        ).offset(skip).limit(limit).all()
```

---

## 8. Frontend Changes

### New Components

**Authentication Components:**
- `app/(auth)/login/page.tsx` - Login page
- `app/(auth)/register/page.tsx` - Registration page
- `components/auth/login-form.tsx` - Login form component
- `components/auth/register-form.tsx` - Registration form component

**Layout Components:**
- `components/layout/sidebar.tsx` - Main navigation sidebar
- `components/layout/header.tsx` - Top header with user menu
- `components/layout/ai-chat-panel.tsx` - Left AI chat panel (placeholder)

**Client Management Components:**
- `app/(dashboard)/clients/page.tsx` - Clients list page
- `app/(dashboard)/clients/new/page.tsx` - New client page
- `app/(dashboard)/clients/[id]/page.tsx` - Client detail page
- `components/clients/client-table.tsx` - Clients data table
- `components/clients/client-form.tsx` - Client create/edit form
- `components/clients/document-upload.tsx` - Document upload component

**Dashboard Components:**
- `app/(dashboard)/page.tsx` - Main dashboard
- `components/dashboard/stats-card.tsx` - KPI card component
- `components/dashboard/recent-activity.tsx` - Recent activity list

**UI Components (shadcn/ui):**
- Install: button, input, label, card, table, form, dialog, dropdown-menu, avatar, badge

### Page Updates

**New Pages:**
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Main dashboard (protected)
- `/clients` - Clients list (protected)
- `/clients/new` - New client form (protected)
- `/clients/[id]` - Client details (protected)

**Layout Structure:**
- Three-column layout for dashboard pages (AI panel, sidebar, main content)
- Responsive collapse on mobile
- Protected routes with authentication middleware

### State Management

**Auth Context:**
```typescript
// contexts/auth-context.tsx
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}
```

**React Query for Data Fetching:**
- Use `@tanstack/react-query` for server state
- Cache client data, user data
- Automatic refetching and background updates
- Optimistic updates for mutations

---

## 9. Implementation Plan

### Phase 1.1: Backend Foundation (Week 1-2)
1. **Project Setup**
   - [ ] Initialize FastAPI project structure
   - [ ] Setup virtual environment and dependencies
   - [ ] Configure database connections (PostgreSQL, MongoDB, Redis)
   - [ ] Setup Alembic for migrations
   - [ ] Configure environment variables

2. **Database Schema**
   - [ ] Create SQLAlchemy models (Company, User, Client, Permission, etc.)
   - [ ] Create initial Alembic migration
   - [ ] Run migration and verify tables
   - [ ] Create seed data script
   - [ ] Setup MongoDB connection and indexes

3. **Authentication System**
   - [ ] Implement password hashing utilities
   - [ ] Create JWT token generation/validation
   - [ ] Implement OAuth2 password flow
   - [ ] Create auth middleware
   - [ ] Implement role-based permission checks

4. **Core API Endpoints**
   - [ ] Implement auth endpoints (register, login, refresh, logout)
   - [ ] Implement user endpoints
   - [ ] Implement client endpoints
   - [ ] Implement company endpoints
   - [ ] Add request validation with Pydantic schemas

5. **Testing & Documentation**
   - [ ] Write unit tests for auth system
   - [ ] Write integration tests for API endpoints
   - [ ] Verify auto-generated OpenAPI docs
   - [ ] Add CORS configuration

### Phase 1.2: Frontend Foundation (Week 3-4)
1. **Project Setup**
   - [ ] Initialize Next.js 14 with TypeScript
   - [ ] Setup Tailwind CSS
   - [ ] Install shadcn/ui components
   - [ ] Configure environment variables
   - [ ] Setup folder structure (app router)

2. **Authentication UI**
   - [ ] Create login page and form
   - [ ] Create registration page and form
   - [ ] Implement auth context provider
   - [ ] Create authentication API client
   - [ ] Add protected route middleware
   - [ ] Implement token refresh logic

3. **Layout Components**
   - [ ] Create main layout with three-column structure
   - [ ] Implement sidebar navigation
   - [ ] Create header with user menu
   - [ ] Add placeholder AI chat panel
   - [ ] Make layout responsive

4. **Client Management UI**
   - [ ] Create clients list page with data table
   - [ ] Implement pagination and search
   - [ ] Create new client form
   - [ ] Create client detail page
   - [ ] Implement document upload component
   - [ ] Add form validation with Zod

5. **Dashboard**
   - [ ] Create dashboard page
   - [ ] Add stats cards (total clients, recent activity)
   - [ ] Implement data fetching with React Query
   - [ ] Add loading and error states

### Phase 1.3: Integration & Testing (Week 5-6)
1. **Integration**
   - [ ] Connect frontend to backend API
   - [ ] Test authentication flow end-to-end
   - [ ] Test client CRUD operations
   - [ ] Verify multi-tenant data isolation
   - [ ] Test document upload flow

2. **Testing**
   - [ ] Run automated backend tests
   - [ ] Perform manual UI testing
   - [ ] Test on mobile devices
   - [ ] Test on different browsers
   - [ ] Fix identified bugs

3. **Documentation**
   - [ ] Document API endpoints
   - [ ] Create setup instructions
   - [ ] Document environment variables
   - [ ] Create user guide for basic features

### Phase 1.4: Deployment Preparation (Week 7-8)
1. **DevOps Setup**
   - [ ] Create Dockerfile for backend
   - [ ] Create Dockerfile for frontend
   - [ ] Setup docker-compose for local development
   - [ ] Configure CI/CD pipeline (GitHub Actions)
   - [ ] Setup staging environment

2. **Security Hardening**
   - [ ] Enable HTTPS
   - [ ] Add rate limiting
   - [ ] Implement CSRF protection
   - [ ] Add security headers
   - [ ] Review and fix security vulnerabilities

3. **Performance Optimization**
   - [ ] Add database indexes
   - [ ] Implement Redis caching
   - [ ] Optimize API response times
   - [ ] Optimize frontend bundle size
   - [ ] Add monitoring (Sentry)

4. **Final Testing**
   - [ ] Load testing
   - [ ] Security audit
   - [ ] Accessibility testing
   - [ ] Cross-browser testing
   - [ ] User acceptance testing

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking

**Weekly Stand-ups:**
- Update task completion status every Friday
- Report blockers and risks
- Adjust timeline if needed

**Automated Testing:**
- All tests must pass before marking tasks complete
- Code coverage target: 80%

**Code Review:**
- All code must be reviewed before merging
- Follow PR template

---

## 11. File Structure & Organization

### Backend Structure
```
backend/
├── alembic/                 # Database migrations
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/   # Route handlers
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── clients.py
│   │       │   └── companies.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── security.py      # Auth utilities
│   │   └── dependencies.py  # FastAPI dependencies
│   ├── models/              # SQLAlchemy models
│   │   ├── company.py
│   │   ├── user.py
│   │   ├── client.py
│   │   └── permission.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── client.py
│   │   └── company.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── client_service.py
│   │   └── user_service.py
│   ├── repositories/        # Database access
│   │   ├── client_repository.py
│   │   └── user_repository.py
│   └── utils/               # Helpers
├── tests/
│   ├── test_auth.py
│   ├── test_clients.py
│   └── test_users.py
├── main.py                  # FastAPI app entry point
├── requirements.txt
└── .env.example
```

### Frontend Structure
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── clients/
│   │   │   ├── page.tsx
│   │   │   ├── new/
│   │   │   │   └── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── layout.tsx
├── components/
│   ├── auth/
│   │   ├── login-form.tsx
│   │   └── register-form.tsx
│   ├── clients/
│   │   ├── client-table.tsx
│   │   ├── client-form.tsx
│   │   └── document-upload.tsx
│   ├── dashboard/
│   │   ├── stats-card.tsx
│   │   └── recent-activity.tsx
│   ├── layout/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   └── ai-chat-panel.tsx
│   └── ui/                  # shadcn/ui components
├── contexts/
│   └── auth-context.tsx
├── lib/
│   ├── api.ts               # API client
│   └── utils.ts
├── types/
│   ├── user.ts
│   ├── client.ts
│   └── auth.ts
└── package.json
```

---

## 12. AI Agent Instructions

### Implementation Workflow

🎯 **MANDATORY PROCESS:**

**Rule Management:**
- Read ALL rules in `ai_docs/rules/` before starting implementation
- Follow the mandatory auto-test-fix process
- Create new rules for any errors encountered
- Update `ai_task_template_skeleton.md` when creating new rules

**Task Execution:**
- Follow the implementation plan sequentially
- Update task.md progress as you work
- Test each feature before moving to next
- Use browser_subagent to verify UI works
- Run backend tests after each API implementation

**Quality Checklist Before Completion:**
- [ ] All backend tests passing
- [ ] All frontend builds without errors
- [ ] Tested authentication flow in browser
- [ ] Tested client CRUD in browser
- [ ] Verified UI matches dashboard_visual_description.md
- [ ] API documentation generated and accessible
- [ ] Code reviewed and follows project standards
- [ ] Database migrations successful
- [ ] Multi-tenant isolation verified

### Communication Preferences
- Report progress weekly
- Immediately flag any blockers
- Ask for clarification on unclear requirements
- Provide demos of completed features

### Code Quality Standards
- TypeScript strict mode enabled
- Python type hints required
- ESLint and Prettier configured
- 80%+ test coverage
- No console.log in production code
- All API responses properly typed

---

## 13. Second-Order Impact Analysis

### Impact Assessment

**Concerns:**
- Database schema changes will affect all future phases - must be well-designed
- Authentication system security is critical - any vulnerability affects entire platform
- Multi-tenant isolation bugs could expose data across companies
- Poor API design will be hard to change later

**Performance Concerns:**
- Database query optimization crucial for scalability
- JWT token size affects every API call
- File upload handling affects user experience

**User Workflow Impacts:**
- Login flow must be smooth - first impression matters
- Client creation form must be intuitive
- Error messages must be helpful

**Mitigation:**
- Extensive testing of multi-tenant isolation
- Security audit of authentication system
- Performance testing under load
- UX testing with real users

---

## 14. Mandatory Rules & Best Practices

> **📋 CRITICAL:** Follow ALL rules in `ai_docs/rules/` during implementation.

### 🚨 Critical Process Rules

#### 1. Auto-Test-Fix Process (MOST IMPORTANT)
**File:** `00_MANDATORY_auto_test_fix_process.mdc`

**Checklist:**
- [ ] Read ALL rules before starting
- [ ] Test feature in browser
- [ ] If issues found → Create rule + Fix + Test again
- [ ] Only report success when everything works

#### 2. Auto-Create Rule on Error (MANDATORY)
**File:** `01_MANDATORY_auto_create_rule_on_error.mdc`

**Checklist:**
- [ ] Encountered error? Create rule immediately
- [ ] Update ai_task_template_skeleton.md

#### 3. Fix Missing Components (MANDATORY)
**File:** `02_MANDATORY_fix_missing_components.mdc`

**Checklist:**
- [ ] Module not found? Check if file exists
- [ ] Create missing component immediately

#### 4. Always Clean Build (MANDATORY)
**File:** `03_MANDATORY_always_clean_build.mdc`

**Checklist:**
- [ ] Before debugging, clean .next directory

### 🔧 Component & Import Verification

#### 5. Verify Component Imports
**File:** `verify_component_imports.mdc`

**Checklist:**
- [ ] Before importing, verify file exists
- [ ] Use list_dir to confirm

#### 6. Verify Component Exports
**File:** `verify_component_exports.mdc`

**Checklist:**
- [ ] View file to check exports
- [ ] Match import to actual export

### 🔐 Authentication & Security

#### 7. Check Auth Dependencies
**File:** `check_auth_dependencies.mdc`

**Checklist:**
- [ ] Verify auth system exists before using
- [ ] Check both frontend and backend

### 🛠️ Build & Error Handling

#### 8. Build Error Logging
**File:** `build_error_logging.mdc`

**Workflow:**
```powershell
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue
npm run build > build.log 2>&1
Get-Content build.log
```

#### 9. Handle Build Log Encoding
**File:** `handle_build_log_encoding.mdc`

**Checklist:**
- [ ] If encoding error, use `cmd /c type build.log`

#### 10. Analyze Build Failures (MANDATORY)
**File:** `analyze_build_failure.mdc`

**Checklist:**
- [ ] If build fails with exit code 1, capture full logs (`npm run build > log.txt 2>&1`)
- [ ] Read the full log file
- [ ] Run `npx tsc --noEmit` to isolate TypeScript errors

#### 11. Zod Resolver Type Mismatch
**File:** `zod_resolver_type_mismatch.mdc`

**Checklist:**
- [ ] Remove `.default()` from schema for controlled form fields
- [ ] Provide explicit `defaultValues` in `useForm`
- [ ] Verify `z.infer<typeof schema>` matches `useForm<Type>`

### 🎨 UI/UX Consistency

#### 12. Visual Design Consistency
**File:** `visual_design_consistency.mdc`

**Checklist:**
- [ ] Read dashboard_visual_description.md before creating UI
- [ ] Use specified colors, fonts, layouts
- [ ] Verify design matches in browser

#### 13. Interactive Elements Must Have Actions
**File:** `interactive_elements_must_have_actions.mdc`

**Checklist:**
- [ ] All buttons have onClick handlers
- [ ] All links have valid href

### 🏗️ Component Architecture

#### 14. Verify Modal Imports and Build
**File:** `verify_modal_imports_and_build.mdc`

**Checklist:**
- [ ] Check modal exports (default vs named)
- [ ] Ensure "use client" directive
- [ ] Run build after adding modal

### 🌐 Server & Browser Testing

#### 15. Check Dev Server Status
**File:** `check_dev_server_status.mdc`

**Checklist:**
- [ ] Before browser testing, verify server running
- [ ] Use Test-NetConnection to check port

---

## 15. Definition of Done

Phase 1 is complete when:
- ✅ Backend API running and accessible
- ✅ Frontend Next.js running and accessible
- ✅ User can register and login successfully
- ✅ User can create, view, update, delete clients
- ✅ User can upload documents for clients
- ✅ Admin can view dashboard with statistics
- ✅ Multi-tenant isolation verified (data doesn't leak between companies)
- ✅ All automated tests passing
- ✅ API documentation accessible at /docs
- ✅ UI matches dashboard_visual_description.md design
- ✅ Application responsive on mobile, tablet, desktop
- ✅ Code reviewed and merged to main branch
- ✅ Deployed to staging environment

---

**Task Version**: 1.0  
**Created**: December 2025  
**Estimated Duration**: 8 weeks (2 months)  
**Status**: Ready for Implementation
