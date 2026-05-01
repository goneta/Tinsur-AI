# Todo

## Tinsur-AI production-readiness assessment

- [ ] Re-read the Tinsur-AI repository workflow guidance before making repository-based observations.
- [ ] Confirm the active repository path and current branch state.
- [ ] Inspect the application structure to identify already implemented modules for quotes, policies, users, companies, clients, agents, payments, and support workflows.
- [ ] Identify missing capabilities for car insurance, travel insurance, and home insurance.
- [ ] Identify missing cross-cutting capabilities: underwriting, rating, policy lifecycle, claims, documents, payments, compliance, audit, security, observability, and admin operations.
- [ ] Produce a prioritized roadmap with practical milestones and recommended next implementation order.

## Tinsur.AI Fourth Backend Milestone Checklist

- [x] Re-read `/home/ubuntu/skills/tinsur-ai-repo-workflow/SKILL.md` and follow the repository workflow.
- [x] Verify `/home/ubuntu/Tinsur-AI-kenbot-milestones-1777649530/` is on `kenbot_branche` with a clean working tree before implementation.
- [x] Inspect existing backend models, schemas, services, API routing, and tests for product, quote, policy, and AI context patterns.
- [x] Implement versioned product catalog models for car, travel, and home insurance.
- [x] Implement coverage, coverage option, rating factor, underwriting rule, and quote wizard schema support.
- [x] Add product admin/API endpoints for catalog lookup and CRUD-style configuration.
- [x] Add seed/default product catalog definitions for car, travel, and home insurance.
- [x] Extend AI tenant context so agents are aware of active product and coverage catalog definitions.
- [x] Add focused tests using lightweight isolated fixtures rather than broad incompatible database fixtures.
- [x] Run syntax checks, Alembic head validation, and targeted pytest validation.
- [x] Create `FOURTH_BACKEND_MILESTONE_VALIDATION.txt` documenting scope and validation evidence.
- [ ] Commit changes on `kenbot_branche` and push synchronized heads to `main`, `master`, and `kenbot_branche` without exposing credentials.
