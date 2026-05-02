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
- [x] Commit changes on `kenbot_branche` and push synchronized heads to `main`, `master`, and `kenbot_branche` without exposing credentials.

## Tinsur.AI Fifth Backend Milestone Checklist

- [x] Re-read `/home/ubuntu/skills/tinsur-ai-repo-workflow/SKILL.md` and follow the repository workflow for Milestone 5.
- [x] Confirm the repository is on the preferred branch and synchronized with the Milestone 4 remote heads.
- [x] Identify the intended Milestone 5 scope from existing roadmap notes, validation files, and repository structure.
- [x] Inspect Milestone 4 product catalog engine integration points for the next implementation layer.
- [x] Implement Milestone 5 backend capabilities using existing model, schema, service, endpoint, and migration conventions.
- [x] Add focused tests that validate the new Milestone 5 behavior without relying on unrelated incompatible fixtures.
- [x] Run syntax checks, Alembic validation where applicable, and targeted pytest checks.
- [x] Create `FIFTH_BACKEND_MILESTONE_VALIDATION.txt` documenting scope, files changed, and validation evidence.
- [x] Commit Milestone 5 changes locally on the preferred branch.
- [x] Report the implementation status and ask before remote synchronization if credentials are required.

## Milestone 5 Remote Synchronization

- [x] Push Milestone 5 commit `72803ea572f0f6ede96f4bf32604b47da6548157` to `origin/kenbot_branche`.
- [x] Push Milestone 5 commit `72803ea572f0f6ede96f4bf32604b47da6548157` to `origin/main`.
- [x] Push Milestone 5 commit `72803ea572f0f6ede96f4bf32604b47da6548157` to `origin/master`.
- [x] Fetch and verify all three remote heads match the local Milestone 5 commit.
- [ ] Confirm the local repository is clean after synchronization.

## GitHub Authentication Enablement

- [x] Inspect local GitHub CLI and Git credential state without exposing secrets.
- [x] Guide the user through the required sensitive authentication step if credentials are not already available.
- [x] Verify authenticated access to the target GitHub remote.
- [x] Push Milestone 5 commit `72803ea572f0f6ede96f4bf32604b47da6548157` to `origin/kenbot_branche`, `origin/main`, and `origin/master`.
- [x] Verify all three remote heads match the local Milestone 5 commit; local status contains only checklist traceability updates in `todo.md`.

## Token-Based Remote Synchronization Attempt

- [x] Use the fresh user-provided GitHub PAT for this synchronization attempt only; do not commit or persist the token value.
- [x] Push committed Milestone 5 changes from local `kenbot_branche` to remote `kenbot_branche`, `main`, and `master`.
- [x] Confirm all three remotes resolve to Milestone 5 commit `72803ea572f0f6ede96f4bf32604b47da6548157`.

## Tinsur.AI Sixth Backend Milestone Checklist

- [x] Re-read `/home/ubuntu/skills/tinsur-ai-repo-workflow/SKILL.md` and follow the repository workflow for Milestone 6.
- [x] Confirm the repository is on `kenbot_branche` and identify any local traceability-only changes before implementation.
- [x] Inspect existing roadmap, validation artifacts, models, schemas, services, endpoints, agents, and tests to define the Milestone 6 scope.
- [x] Implement the selected Milestone 6 backend capability using tenant-safe repository conventions.
- [x] Add focused tests that validate the new Milestone 6 behavior without relying on broad incompatible fixtures.
- [x] Run syntax checks and targeted pytest validation.
- [x] Create `SIXTH_BACKEND_MILESTONE_VALIDATION.txt` documenting scope, files changed, and validation evidence.
- [x] Update `todo.md` for traceability.
- [x] Commit Milestone 6 changes locally on `kenbot_branche`.
- [ ] Report implementation status and request or use approved credentials before remote synchronization.

### Milestone 6 Scope Decision

Milestone 6 will implement **automatic policy acquisition orchestration** on top of the Milestone 4 product catalog and Milestone 5 product quote engine. The scope is to turn a catalog-backed customer recommendation into a persisted first-class quote, policy-ready underwriting snapshot, optional immediate policy issuance, and aligned conversational policy-agent conversion path. This directly supports the product goal that a customer can enter personal and car details, receive an automatic quote decision, and obtain an insurance policy without a manually assembled backend workflow.
