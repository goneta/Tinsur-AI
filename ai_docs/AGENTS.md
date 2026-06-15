# DOX framework

## Purpose

- Owns AI task templates and reusable project rules for automated coding, verification, recovery, and UI consistency.

## Ownership

- `rules/` contains durable rule snippets that agents should consult when matching issues arise.
- `task-templates/` contains phase plans and repeatable task briefs.

## Local Contracts

- Keep rules operational and current; remove stale recovery notes instead of layering contradictory guidance.
- Do not record one-off task diaries here unless they become reusable process guidance.

## Work Guidance

- Prefer concise, named rules with clear trigger conditions and verification expectations.
- When code changes reveal a reusable failure pattern, add or update a rule only after confirming it is stable.

## Verification

- No standalone verification currently exists for these docs.

## Child DOX Index

- No child AGENTS.md files currently.
