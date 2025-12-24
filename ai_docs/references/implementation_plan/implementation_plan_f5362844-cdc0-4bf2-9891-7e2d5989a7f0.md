# Implementation Plan: Fix Database Migrations (Phase 7 & Claims)

This plan focuses on rectifying inconsistencies in the database migration history, specifically restoring the `claims` table and properly integrating all Phase 7 tables into Alembic.

## Proposed Changes

### [Backend] Database & Migrations

#### [NEW] [Migration Version](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/alembic/versions/)
- Create a new migration file (e.g., `restoring_phase_7_tables.py`) that includes `op.create_table` commands for:
    - `claims`
    - `inter_company_shares`
    - `tickets`
    - `referrals`
    - `loyalty_points`
    - `telematics_data`
    - `ml_models`
- Ensure all foreign keys, indexes, and unique constraints match the SQLAlchemy models.

#### [MODIFY] [main.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/main.py)
- Evaluate removing `Base.metadata.create_all(bind=engine)` to enforce migration-based schema updates.

## Verification Plan

### Automated Tests
- **Alembic History**: Run `alembic history` to verify the new migration is properly sequenced.
- **Dry Run Upgrade**: Run `alembic upgrade head --sql` to inspect the generated SQL.
- **Execution**: Run `alembic upgrade head`.
- **Logic Consistency**: Re-run `verify_lifecycle.py` and `verify_advanced_logic.py` to confirm everything still works after the migration fix.

### Manual Verification
- Use a database tool or inspection script to verify the table structures in the database.
