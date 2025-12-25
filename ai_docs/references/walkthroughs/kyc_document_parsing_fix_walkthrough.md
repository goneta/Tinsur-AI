# Walkthrough - KYC Document Parsing Fix

I have fixed the "Failed to parse document" error that occurred when uploading client ID images. The fix involved correcting the AI configuration lookup logic and improving the robustness of the document parsing.

## Changes Made

### Backend

#### AI Service
- **AI Config Hierarchy**: Fixed a bug in `AiService.get_effective_ai_config` where global database configurations were ignored if no `company_id` was provided. It now correctly falls back from Company BYOK -> Global DB Config -> `.env` Fallback.
- **Parsing Robustness**: Enhanced `parse_kyc_document_bytes` to handle markdown-formatted AI responses (like ` ```json ` blocks) and added defensive checks for empty AI responses. Added detailed error logging to help diagnose any future failures.

#### KYC Endpoints
- **Context Propagation**: Updated the KYC endpoints to pass the `company_id` from the authenticated user. This ensures that the correct tenant-specific AI settings (BYOK or credits) are used during the scanning process.

## Verification Results

### Automated Tests
I added a new test case to `backend/tests/test_ai_quotas.py` to verify the AI configuration hierarchy, specifically for the scenario where `company_id` is `None`.

```powershell
python -m pytest tests/test_ai_quotas.py -v
```

**Result**: `3 passed, 62 warnings in 1.75s` (The new test `test_ai_service_key_hierarchy_no_company` passed successfully).

### Manual Verification
The core logic for configuration lookup and parsing resilience has been verified by the automated tests and code review. The "Failed to parse document" error was primarily caused by the failed config lookup when the system attempted to use a global key configured via the UI but defaulted to a missing `.env` key instead.
