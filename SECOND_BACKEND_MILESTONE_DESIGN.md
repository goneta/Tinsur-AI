# Second Backend Milestone Design

## Objective

The second backend milestone connects the automobile underwriting snapshot to a safer quote lifecycle. A quote should only move into a payable and issuable state when the stored underwriting result is **approved**, current, and policy-ready. Policy issuance should be idempotent, should preserve the underwriting payload in the policy details, and should leave policy document generation ready to run through the existing policy service hook.

## Existing Constraints

The current backend already persists `QuoteUnderwritingSnapshot` with the normalized payload, decision snapshot, premium breakdown, and `policy_ready_payload`. The quote approval endpoint currently accepts a draft quote and immediately creates an active policy. The payment subsystem is policy-centric because `Payment.policy_id` is required, so a pure pre-policy quote payment would require a wider database migration. For this milestone, the lowest-risk backend implementation is therefore to make quote approval create an active policy only after validating the underwriting snapshot, and to create a pending payment request tied to the issued policy when a conversion endpoint includes payment information.

## Flow Design

| Step | Component | Milestone Behavior |
|---|---|---|
| 1 | Underwriting service | Keep persisting `QuoteUnderwritingSnapshot` as the authoritative decision artifact. |
| 2 | Quote service | `accept_quote` must validate that an underwriting snapshot exists, is approved, is not expired, and matches the final premium before marking the quote accepted. |
| 3 | Policy service | `create_from_quote` must be idempotent, must reject missing/non-approved snapshots, and must copy snapshot identifiers, decision payload, premium breakdown, vehicle/client references, and required documents into `policy.details`. |
| 4 | Quote endpoints | `/approve` and `/convert` should return structured policy/payment readiness data and reject referred/declined/missing underwriting cases instead of creating policies blindly. |
| 5 | Payment flow | Because payments are policy-bound, `convert` can optionally create and process a policy payment after issuance. Webhook and direct completion hooks should activate document/accounting side effects without duplicating policy creation. |
| 6 | Documents | The existing `document_service.generate_documents` call remains the document-generation hook; enriched `policy.details` gives templates the data needed for vehicle, underwriting, and required-document sections. |

## Implementation Decisions

This milestone will not make destructive schema changes to `payments.policy_id`, because doing so would require broad repository, response-schema, reporting, and ledger changes. Instead, the implementation adds service-level validation and idempotency around existing models, enriches policy details with the underwriting snapshot, and adds optional payment processing to quote conversion while preserving existing payment API behavior.

The public contract should remain backward compatible where possible. Existing `/quotes/{id}/approve` continues to issue a policy, but it now requires a valid approved snapshot. Existing `/quotes/{id}/convert` continues to convert an accepted quote, while optionally accepting payment method, gateway, initial payment amount, and payment details to create/process the first premium payment.
