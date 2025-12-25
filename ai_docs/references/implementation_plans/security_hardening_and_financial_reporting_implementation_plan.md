# Phase 8: Optimization & Launch - Hardening & Financials

This plan covers the transition to Phase 8, focusing on Multi-tenant Security Isolation and completing the Phase 6 Financial Reporting requirements (Profit & Loss and Balance Sheet).

## User Review Required

> [!IMPORTANT]
> **Data Privacy**: We are hardening the "Multi-Tenant" boundary. Specialist agents will now strictly reject requests that attempt to access data outside their assigned `company_id`.
> 
> **Accounting Accuracy**: P&L and Balance Sheet reports rely on the General Ledger (`ledger_entries`). Ensure that all financial events (Payments, Payroll, etc.) are correctly posting to the ledger for accurate reporting.

## Proposed Changes

### [Component] Security & Multi-Tenancy (Hardening)

#### [MODIFY] [agent_executor.py](file:///C:/Users/user/Desktop/Tinsur.AI/backend/agents/a2a_claims_agent/agent_executor.py)
- Update all queries to include `Policy.company_id == context_company_id`.
- Ensure `company_id` is extracted from metadata reliably.

#### [MODIFY] [agent_executor.py](file:///C:/Users/user/Desktop/Tinsur.AI/backend/agents/a2a_quote_agent/agent_executor.py) (and others)
- Audit and apply similar `company_id` filtering to all specialist agents.

---

### [Component] Financial Reporting (Backend)

#### [MODIFY] [accounting_service.py](file:///C:/Users/user/Desktop/Tinsur.AI/backend/app/services/accounting_service.py)
- Implement `get_profit_loss(company_id, start_date, end_date)`.
- Implement `get_balance_sheet(company_id, as_of_date)`.

#### [MODIFY] [accounting.py](file:///C:/Users/user/Desktop/Tinsur.AI/backend/app/api/v1/endpoints/accounting.py)
- Add entries for `/profit-loss` and `/balance-sheet`.

---

### [Component] Financial Reporting (Frontend)

#### [MODIFY] [accounting-api.ts](file:///C:/Users/user/Desktop/Tinsur.AI/frontend/lib/accounting-api.ts)
- Add methods for `getProfitLoss` and `getBalanceSheet`.

#### [MODIFY] [page.tsx](file:///C:/Users/user/Desktop/Tinsur.AI/frontend/app/dashboard/financials/page.tsx)
- Add "Profit & Loss" and "Balance Sheet" tabs.
- Implement report-style tables for these views.
- Add date filters for the P&L report.

## Verification Plan

### Automated Tests
- Scripted tests to attempt cross-tenant ID access via specialist agents (expect failure).
- Unit tests for P&L calculation logic in `AccountingService`.

### Manual Verification
- Log in as Company A user, attempt to query Company B's policy ID via the AI Chat.
- Verify that P&L report correctly matches the sum of transactions in the Ledger.
- Verify Balance Sheet balances (Assets = Liabilities + Equity).
