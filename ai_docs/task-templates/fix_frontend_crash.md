# Task: Resurrect Frontend Server

## 🚨 Mandatory Pre-Implementation Checklist
- [x] Read all rules in `ai_docs/rules/`.
- [x] Checked for existing rules (`rule_db_connection.mdc` - irrelevant here, but checked).
- [x] Identified potential errors: Frontend process died.
- [x] Confirmed adherence to "Rules-First".

## 📋 Task Overview
**Objective**: Restore access to the website (`localhost:3000`).
**Context**: User gets "Site inaccessible". Metadata shows `npm run dev` is no longer running.

## 🛠 Required Rules & Constraints
- Rule: **Automatic Command Execution** (Restart automatically).

## 📝 Implementation Plan
- [ ] **Step 1**: Restart `npm run dev`.
- [ ] **Step 2**: Verify it listens on port 3000.

## ✅ Verification & Testing Logic
- [ ] **Automated Tests**: None (Visual verification).
- [ ] **Success Criteria**: Terminal output shows "Ready on http://localhost:3000".

## 🔄 Post-Task Update
- [ ] Update `task.md`.
