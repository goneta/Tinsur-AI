# Task: Fix Settings Page Build Error (Missing Export)

## 🚨 Mandatory Pre-Implementation Checklist
- [x] Read all rules in `ai_docs/rules/`.
- [x] Checked for existing rules related to this task.
- [x] Identified potential errors/risks: Import/Export mismatch in TypeScript.
- [x] Confirmed strict adherence to "Rules-First" workflow.

## 📋 Task Overview
**Objective**: Fix the `Export getUsers doesn't exist` error in `settings/page.tsx`.
**Context**: The `Settings` page is trying to import `getUsers` from `user-api.ts`, but the module likely exports differently (e.g., as a default object `userApi` or different named exports).

## 🛠 Required Rules & Constraints
- Rule: **Verify Component Exports** (Implicit rule: always check exports match imports).

## 📝 Implementation Plan
- [ ] **Step 1**: Read `frontend/lib/user-api.ts` to identify correct exports.
- [ ] **Step 2**: Read `frontend/app/dashboard/settings/page.tsx` to see incorrect usage.
- [ ] **Step 3**: Update `frontend/app/dashboard/settings/page.tsx` to use the correct API method.

## ✅ Verification & Testing Logic
- [ ] **Automated Tests**: TypeScript Compilation (`npm run build` or checking dev server output).
- [ ] **Manual Verification**: User confirms error is gone.

## 🔄 Post-Task Update
- [ ] Did any errors occur? If yes, create new rule.
- [ ] Update `task.md`.
