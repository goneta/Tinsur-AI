# Task: Debug Persistent Login Connection Error V2

## 🚨 Mandatory Pre-Implementation Checklist
- [x] Read all rules in `ai_docs/rules/`.
- [x] Checked for existing rules (`rule_db_connection.mdc`).
- [x] Identified potential errors: DB down, Backend crash, seeding lock.
- [x] Confirmed adherence to "Rules-First".

## 📋 Task Overview
**Objective**: definitively resolve "Connection Error: Login failed".
**Context**: User reported this error previously. We restarted DB. Error persists or recurred.

## 🛠 Required Rules & Constraints
- Rule: **Verify Connection Before Start**.
- Rule: **Auto-Test** `test_login.py`.

## 📝 Implementation Plan
- [ ] **Step 1**: Run `backend/scripts/check_db.py`.
- [ ] **Step 2**: Check Backend Process (`uvicorn`).
- [ ] **Step 3**: Check `test_login.py` output.
- [ ] **Step 4**: Restart Backend if needed.

## ✅ Verification & Testing Logic
- [ ] **Automated Tests**: `test_login.py` returns 200.
- [ ] **Manual Verification**: Login via UI.

## 🔄 Post-Task Update
- [ ] Update rules if new cause found.
