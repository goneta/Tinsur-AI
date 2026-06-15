# DOX framework

## Purpose

- Owns standalone A2A, ADK, LangGraph, RAG, and domain-specific agent packages.

## Ownership

- Each agent folder owns its `agent_executor.py`, `tools.py`, `models.py`, `__main__.py`, and local package wiring.
- Shared A2A protocol/server support outside this folder is owned by `backend/a2a/` under the parent backend contract.

## Local Contracts

- Preserve each agent package's public entry points and executor contract.
- Maintain each important agent source file's sibling `.md` documentation file alongside code changes.
- Keep tool side effects explicit, authenticated where required, and compatible with backend services.
- Do not weaken backend security or action-control behavior from agent code.

## Work Guidance

- Reuse existing tool/model patterns from nearby agents before introducing new agent structure.
- Keep domain agents focused on their named domain such as quote, policy, finance, claims, telematics, support, referrals, tickets, OCR, or loyalty.

## Verification

- Run relevant backend tests under `backend/tests/` after agent changes.
- Use targeted verification scripts such as `python verify_*agent*.py` from `backend/` when they match the changed agent.

## Child DOX Index

- No child AGENTS.md files currently.
