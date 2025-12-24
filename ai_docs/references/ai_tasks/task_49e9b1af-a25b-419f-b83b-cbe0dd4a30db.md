# Master Project Task List - Educational SaaS

This task list covers the roadmap for the **26-Module SaaS** described in `education_saas_plan_en.html`.

## Phase 1: The Foundation (Current Focus)
- [x] **1. Project Initialization & Architecture** <!-- id: 0 -->
    - [x] Initialize Git Repository <!-- id: 1 -->
    - [x] **Backend**: Setup FastAPI + Poetry + Docker <!-- id: 2 -->
    - [x] **Frontend**: Setup Next.js 14 + Tailwind + Shadcn/UI <!-- id: 3 -->
    - [x] **Database**: Configure SQLite (Local) & MongoDB Atlas (Cloud) <!-- id: 4 -->
- [x] **2. Core System & Auth** <!-- id: 5 -->
    - [x] Design Multi-tenant DB Schema (Schools/Tenants) <!-- id: 6 -->
    - [x] Implement RBAC (Role-Based Access Control) <!-- id: 7 -->
    - [x] API: Auth Endpoints (Login/Register/Recover) <!-- id: 8 -->
    - [x] **System Configuration (Dynamic Data)** <!-- id: 33 -->
        - [x] Model: `ReferenceData` for configurable Dropdowns/Levels <!-- id: 34 -->
        - [x] Seed: African Education Systems (Maternelle -> PhD) <!-- id: 35 -->
        - [x] API: CRUD for Reference Data (Admin control) <!-- id: 36 -->
    - [/] **Multilanguage Core** <!-- id: 37 -->
        - [/] Frontend: Setup `next-intl` <!-- id: 38 -->
        - [ ] Backend: Locale handling in API <!-- id: 39 -->
- [/] **3. Module: Administrative (MVP)** <!-- id: 9 -->
    - [x] Student Registration Flows (Backend) <!-- id: 10 -->
    - [ ] Student Profile Management <!-- id: 11 -->
    - [ ] Class & Section Configuration <!-- id: 12 -->
- [ ] **4. Module: Educational (MVP)** <!-- id: 13 -->
    - [ ] Course/Subject Management <!-- id: 14 -->
    - [ ] Timetable Creation <!-- id: 15 -->
    - [ ] Attendance Tracking <!-- id: 16 -->
    - [ ] Grading System Basic <!-- id: 17 -->
- [ ] **5. Module: Financial (MVP)** <!-- id: 18 -->
    - [ ] Fee Type Configuration <!-- id: 19 -->
    - [ ] Student Billing & Invoicing <!-- id: 20 -->
    - [ ] Payment Recording (Cash/Check) <!-- id: 21 -->

## Phase 2: Engagement & Operations
- [ ] **Module: Communication** (SMS, Email, Chat) <!-- id: 22 -->
- [ ] **Module: HR Management** (Staff, Payroll, Contracts) <!-- id: 23 -->
- [ ] **Module: Infrastructure** (Room Booking, Maintenance) <!-- id: 24 -->
- [ ] **Module: Payments** (Mobile Money Integration) <!-- id: 25 -->
- [ ] **Module: Docs** (Shared Document Space) <!-- id: 26 -->

## Phase 3: Advanced Features & AI
- [ ] **Module: AI Agent Integration** (RAG, Helpers) <!-- id: 27 -->
- [ ] **Module: Logistics** (Transport, Cafeteria, Library) <!-- id: 28 -->
- [ ] **Module: Tech** (QR Codes, E-Signatures) <!-- id: 29 -->

## Phase 4: Ecosystem
- [ ] **Module: Ministry Access** (National Reports) <!-- id: 30 -->
- [ ] **Module: API & Integrations** <!-- id: 31 -->
- [ ] **Module: Niche Management** (Health, Discipline, Exams, Partners, IT, CCTV, Parking) <!-- id: 32 -->
