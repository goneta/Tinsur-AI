---
name: driver-card-management
description: Principles and patterns for automatic driver card generation, idempotency, and M2M linkage.
---

# Driver Card Management Skill

This skill defines the standards for automatic entity generation in Tinsur.AI, specifically focusing on the Client registration flow and Driver Card provisioning.

## Core Principles

### 1. Idempotency (The "Rescue" Pattern)
Always assume a registration or login attempt might be a "retry" of a partially failed setup.
- **Rule**: Before creating a `Client` or `Driver` card, check if the `User` already exists but lacks these profiles.
- **Implementation**: In `SocialAuthService` or equivalent, if `user.role == 'client'`, check for an existing `Client` record. If missing, trigger the provisioning logic immediately.

### 2. Atomic Persistence
Avoid "orphaned" records where a User is created but their Profile is not.
- **Rule**: Use `db.flush()` during intermediate steps to get IDs, but RESERVE `db.commit()` for the very end of the entire flow (User -> Client -> Driver -> Linkage).
- **Benefit**: Ensures that if any part of the generation fails, the entire transaction rolls back, preventing partial registrations.

### 3. Model Robustness (Soft Constraints)
Automatic generation should not fail due to missing optional biographical data.
- **Rule**: `ClientDriver` and similar automatically generated models must have `nullable=True` for non-essential fields (address, license number, etc.).
- **Strategy**: Allow the creation of an "Incomplete" card during signup, which the user can later enrich through the portal.

### 4. M2M Linkage Handling
Establish relationships at the right layer.
- **Rule**: Link clients to companies via the `client_company` M2M table during the entity generation phase, NOT just at the User level.
- **Context**: Ensure the intended `company_id` is passed through the service layer to maintain proper organizational context.

## Implementation Checklist

- [ ] Check for existing User record (Idempotency)
- [ ] Check for existing Client record for that User
- [ ] Ensure `ClientService.create_client` is called with correct context
- [ ] Verify `_create_automatic_driver` handles M2M `companies.append()`
- [ ] Single `db.commit()` at the API/Service entry point
- [ ] Standardized Token response including the `user` object

## Debugging Patterns
When driver cards are missing:
1. Use `find_orphans.py` to check for users without client profiles.
2. Check `ERROR_CLIENT_SERVICE` logs for swallowed exceptions in `_create_automatic_driver`.
3. Verify if `db.commit()` was called after the service execution.
