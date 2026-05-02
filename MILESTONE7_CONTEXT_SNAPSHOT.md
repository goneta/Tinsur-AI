## Branch and status
kenbot_branche
 M todo.md
?? MILESTONE7_CONTEXT_SNAPSHOT.md

## Recent commits
4584566 Implement sixth backend milestone acquisition flow
72803ea Implement product quote engine milestone
48a536d Implement product catalog engine milestone
cb9e201 refactor: replace debug print() with proper logger calls in social auth service
ffffba3 ci: add frontend Docker build and deploy to CI/CD pipeline
39d8787 feat: Next.js frontend Dockerfile + docker-compose service
695f151 feat: WebSocket streaming in main AI agent left-panel
2a1ebf6 Merge milestone AI context into master

## Milestone and validation artifacts
./FIFTH_BACKEND_MILESTONE_VALIDATION.txt
./FOURTH_BACKEND_MILESTONE_VALIDATION.txt
./MILESTONE6_CONTEXT_SNAPSHOT.md
./MILESTONE7_CONTEXT_SNAPSHOT.md
./SECOND_BACKEND_MILESTONE_DESIGN.md
./SECOND_BACKEND_MILESTONE_VALIDATION.txt
./SIXTH_BACKEND_MILESTONE_VALIDATION.txt
./THIRD_BACKEND_MILESTONE_VALIDATION.txt
./todo.md

## Backend service files
- backend/app/services/__init__.py
- backend/app/services/accounting_service.py
- backend/app/services/ai_context_service.py
- backend/app/services/ai_service.py
- backend/app/services/analytics_service.py
- backend/app/services/archive_service.py
- backend/app/services/auth_service.py
- backend/app/services/claim_service.py
- backend/app/services/client_service.py
- backend/app/services/commission_service.py
- backend/app/services/document_service.py
- backend/app/services/export_service.py
- backend/app/services/import_service.py
- backend/app/services/llm_router.py
- backend/app/services/loyalty_service.py
- backend/app/services/ml_service.py
- backend/app/services/notification_service.py
- backend/app/services/ocr_service.py
- backend/app/services/payment_gateway_api.py
- backend/app/services/payment_service.py
- backend/app/services/payroll_service.py
- backend/app/services/policy_service.py
- backend/app/services/premium_policy_service.py
- backend/app/services/premium_service.py
- backend/app/services/product_catalog_service.py
- backend/app/services/product_policy_acquisition_service.py
- backend/app/services/product_quote_engine_service.py
- backend/app/services/quote_generation_service.py
- backend/app/services/quote_service.py
- backend/app/services/recovery_service.py
- backend/app/services/referral_service.py
- backend/app/services/regulatory_service.py
- backend/app/services/reinsurance_service.py
- backend/app/services/security_service.py
- backend/app/services/social_auth_service.py
- backend/app/services/telematics_service.py
- backend/app/services/twofa_service.py
- backend/app/services/underwriting_service.py

## Backend endpoint files
- backend/app/api/v1/endpoints/__init__.py
- backend/app/api/v1/endpoints/accounting.py
- backend/app/api/v1/endpoints/admin.py
- backend/app/api/v1/endpoints/ai.py
- backend/app/api/v1/endpoints/analytics.py
- backend/app/api/v1/endpoints/api_keys.py
- backend/app/api/v1/endpoints/archive.py
- backend/app/api/v1/endpoints/auth.py
- backend/app/api/v1/endpoints/chat.py
- backend/app/api/v1/endpoints/claims.py
- backend/app/api/v1/endpoints/clients.py
- backend/app/api/v1/endpoints/co_insurance.py
- backend/app/api/v1/endpoints/commissions.py
- backend/app/api/v1/endpoints/companies.py
- backend/app/api/v1/endpoints/dev.py
- backend/app/api/v1/endpoints/documents.py
- backend/app/api/v1/endpoints/employees.py
- backend/app/api/v1/endpoints/financial_reports.py
- backend/app/api/v1/endpoints/help.py
- backend/app/api/v1/endpoints/import_export.py
- backend/app/api/v1/endpoints/inter_company_shares.py
- backend/app/api/v1/endpoints/kyc.py
- backend/app/api/v1/endpoints/loyalty.py
- backend/app/api/v1/endpoints/ml_models.py
- backend/app/api/v1/endpoints/notifications.py
- backend/app/api/v1/endpoints/ocr.py
- backend/app/api/v1/endpoints/payments.py
- backend/app/api/v1/endpoints/payroll.py
- backend/app/api/v1/endpoints/permissions.py
- backend/app/api/v1/endpoints/policies.py
- backend/app/api/v1/endpoints/policy_services.py
- backend/app/api/v1/endpoints/policy_templates.py
- backend/app/api/v1/endpoints/policy_types.py
- backend/app/api/v1/endpoints/portal.py
- backend/app/api/v1/endpoints/pos.py
- backend/app/api/v1/endpoints/premium_policies.py
- backend/app/api/v1/endpoints/product_catalog.py
- backend/app/api/v1/endpoints/qr_verification.py
- backend/app/api/v1/endpoints/quote_elements.py
- backend/app/api/v1/endpoints/quotes.py
- backend/app/api/v1/endpoints/recovery.py
- backend/app/api/v1/endpoints/referrals.py
- backend/app/api/v1/endpoints/regulatory.py
- backend/app/api/v1/endpoints/reinsurance.py
- backend/app/api/v1/endpoints/sales.py
- backend/app/api/v1/endpoints/sales_reports.py
- backend/app/api/v1/endpoints/settings.py
- backend/app/api/v1/endpoints/share_code.py
- backend/app/api/v1/endpoints/social_auth.py
- backend/app/api/v1/endpoints/subscription.py
- backend/app/api/v1/endpoints/tasks.py
- backend/app/api/v1/endpoints/telematics.py
- backend/app/api/v1/endpoints/tickets.py
- backend/app/api/v1/endpoints/translations.py
- backend/app/api/v1/endpoints/twofa.py
- backend/app/api/v1/endpoints/underwriting.py
- backend/app/api/v1/endpoints/users.py
- backend/app/api/v1/endpoints/users_snippet.txt
- backend/app/api/v1/endpoints/validation.py

## Tests
- backend/tests/__init__.py
- backend/tests/check_db.py
- backend/tests/conftest.py
- backend/tests/manual_test_pos.py
- backend/tests/run_verification.py
- backend/tests/test_ai_context_integration.py
- backend/tests/test_ai_quotas.py
- backend/tests/test_analytics.py
- backend/tests/test_auth.py
- backend/tests/test_claim_vision.py
- backend/tests/test_clients.py
- backend/tests/test_compliance_agent.py
- backend/tests/test_compliance_expanded.py
- backend/tests/test_eligibility_logic.py
- backend/tests/test_final_quote_calculation.py
- backend/tests/test_financial_ledger.py
- backend/tests/test_full_phase7_flow.py
- backend/tests/test_payment_flow.py
- backend/tests/test_payroll_engine.py
- backend/tests/test_policy_flow.py
- backend/tests/test_portal_quote_selected_services.py
- backend/tests/test_product_catalog_engine.py
- backend/tests/test_product_quote_engine.py
- backend/tests/test_quote_flow.py
- backend/tests/test_sales_commissions.py
- backend/tests/test_sales_reports.py
- backend/tests/test_second_milestone_flow.py
- backend/tests/test_sixth_milestone_acquisition.py
- backend/tests/test_structured_underwriting.py
- backend/tests/test_topup_flow.py
- backend/tests/verify_a2a.py
- backend/tests/verify_agent_security.py
- backend/tests/verify_business_logic.py
- backend/tests/verify_fees.py
- backend/tests/verify_functional_modules.py
- backend/tests/verify_mandatory_agents.py
- backend/tests/verify_mesh.py
- backend/tests/verify_payroll.py
- backend/tests/verify_persistence.py
- backend/tests/verify_phase7_tools.py
- backend/tests/verify_sharing_logic.py

## Search for renewal, payment, document, claim, notification, endorsement terms
backend/app/api/v1/endpoints/ai.py:45:    elif "déclarer" in text or "sinistre" in text or "claim" in text:
backend/app/api/v1/endpoints/ai.py:46:        intent = "file_claim"
backend/app/api/v1/endpoints/ai.py:48:        action = {"type": "navigate", "target": "claims_new"}
backend/app/api/v1/endpoints/ai.py:50:        intent = "make_payment"
backend/app/api/v1/endpoints/ai.py:52:        action = {"type": "navigate", "target": "payments"}
backend/app/api/v1/endpoints/analytics.py:49:    report_type: str = Query("financial_close", pattern="^(financial_close|claims_summary|policies_summary)$"),
backend/app/api/v1/endpoints/archive.py:2:API endpoints for policy document archive and verification.
backend/app/api/v1/endpoints/archive.py:22:    """Get history of archived document versions for a policy."""
backend/app/api/v1/endpoints/archive.py:27:async def verify_document(
backend/app/api/v1/endpoints/archive.py:34:    Verify the integrity of a policy document.
backend/app/api/v1/endpoints/archive.py:40:    is_valid, archive = service.verify_document_integrity(policy_id, content)
backend/app/api/v1/endpoints/archive.py:48:            "hash": archive.document_hash
backend/app/api/v1/endpoints/claims.py:12:from app.schemas.claim import ClaimCreate, ClaimUpdate, ClaimResponse
backend/app/api/v1/endpoints/claims.py:13:from app.schemas.claim_activity import ClaimActivityCreate, ClaimActivityResponse
backend/app/api/v1/endpoints/claims.py:14:from app.services.claim_service import ClaimService
backend/app/api/v1/endpoints/claims.py:16:from app.models.claim_activity import ClaimActivity
backend/app/api/v1/endpoints/claims.py:21:async def create_claim(
backend/app/api/v1/endpoints/claims.py:22:    claim_data: ClaimCreate,
backend/app/api/v1/endpoints/claims.py:26:    """Create a new claim."""
backend/app/api/v1/endpoints/claims.py:28:    # Ensure claim is created for user's company
backend/app/api/v1/endpoints/claims.py:29:    claim_data.company_id = current_user.company_id
backend/app/api/v1/endpoints/claims.py:30:    if not claim_data.created_by:
backend/app/api/v1/endpoints/claims.py:31:        claim_data.created_by = current_user.id
backend/app/api/v1/endpoints/claims.py:34:        claim = service.create_claim(claim_data)
backend/app/api/v1/endpoints/claims.py:35:        return claim
backend/app/api/v1/endpoints/claims.py:43:async def get_claims(
backend/app/api/v1/endpoints/claims.py:50:    """Get all claims."""
backend/app/api/v1/endpoints/claims.py:52:    claims, total = service.get_claims(
backend/app/api/v1/endpoints/claims.py:58:    return claims
backend/app/api/v1/endpoints/claims.py:60:@router.get("/{claim_id}", response_model=ClaimResponse)
backend/app/api/v1/endpoints/claims.py:61:async def get_claim(
backend/app/api/v1/endpoints/claims.py:62:    claim_id: UUID,
backend/app/api/v1/endpoints/claims.py:66:    """Get a specific claim."""
backend/app/api/v1/endpoints/claims.py:68:    claim = service.get_claim(claim_id)
backend/app/api/v1/endpoints/claims.py:70:    if not claim or claim.company_id != current_user.company_id:
backend/app/api/v1/endpoints/claims.py:75:    return claim
backend/app/api/v1/endpoints/claims.py:77:@router.put("/{claim_id}", response_model=ClaimResponse)
backend/app/api/v1/endpoints/claims.py:78:async def update_claim(
backend/app/api/v1/endpoints/claims.py:79:    claim_id: UUID,
backend/app/api/v1/endpoints/claims.py:84:    """Update a claim."""
backend/app/api/v1/endpoints/claims.py:88:    claim = service.get_claim(claim_id)
backend/app/api/v1/endpoints/claims.py:89:    if not claim or claim.company_id != current_user.company_id:
backend/app/api/v1/endpoints/claims.py:95:    updated_claim = await service.update_claim(claim_id, update_data, current_user.id)
backend/app/api/v1/endpoints/claims.py:96:    return updated_claim
backend/app/api/v1/endpoints/claims.py:100:@router.post("/{claim_id}/analyze", response_model=Dict[str, Any])
backend/app/api/v1/endpoints/claims.py:101:async def analyze_claim_damage(
backend/app/api/v1/endpoints/claims.py:102:    claim_id: UUID,
backend/app/api/v1/endpoints/claims.py:106:    """Trigger AI analysis for claim damage (includes automated fraud check)."""
backend/app/api/v1/endpoints/claims.py:110:    claim = service.get_claim(claim_id)
backend/app/api/v1/endpoints/claims.py:111:    if not claim or claim.company_id != current_user.company_id:
backend/app/api/v1/endpoints/claims.py:118:        results = await service.analyze_claim_damage(claim_id, current_user.id)
backend/app/api/v1/endpoints/claims.py:120:        # Re-fetch claim to get latest fraud updates
backend/app/api/v1/endpoints/claims.py:121:        claim = service.repository.get_by_id(claim_id)
backend/app/api/v1/endpoints/claims.py:122:        results["fraud_score"] = float(claim.fraud_score)
backend/app/api/v1/endpoints/claims.py:123:        results["fraud_details"] = claim.fraud_details
backend/app/api/v1/endpoints/claims.py:132:@router.post("/{claim_id}/analyze-fraud", response_model=Dict[str, Any])
backend/app/api/v1/endpoints/claims.py:133:async def analyze_claim_fraud(
backend/app/api/v1/endpoints/claims.py:134:    claim_id: UUID,
backend/app/api/v1/endpoints/claims.py:138:    """Trigger standalone AI fraud analysis for a claim."""
backend/app/api/v1/endpoints/claims.py:142:    claim = service.get_claim(claim_id)
backend/app/api/v1/endpoints/claims.py:143:    if not claim or claim.company_id != current_user.company_id:
backend/app/api/v1/endpoints/claims.py:150:        results = await service.analyze_claim_fraud(claim_id, current_user.id)
backend/app/api/v1/endpoints/claims.py:159:@router.get("/{claim_id}/activity", response_model=List[ClaimActivityResponse])
backend/app/api/v1/endpoints/claims.py:160:async def list_claim_activity(
backend/app/api/v1/endpoints/claims.py:161:    claim_id: UUID,
backend/app/api/v1/endpoints/claims.py:165:    """List activity for a claim."""
backend/app/api/v1/endpoints/claims.py:167:    claim = service.get_claim(claim_id)
backend/app/api/v1/endpoints/claims.py:168:    if not claim or claim.company_id != current_user.company_id:
backend/app/api/v1/endpoints/claims.py:171:    return db.query(ClaimActivity).filter(ClaimActivity.claim_id == claim_id).order_by(ClaimActivity.created_at.desc()).all()
backend/app/api/v1/endpoints/claims.py:174:@router.post("/{claim_id}/activity", response_model=ClaimActivityResponse)
backend/app/api/v1/endpoints/claims.py:175:async def add_claim_activity(
backend/app/api/v1/endpoints/claims.py:176:    claim_id: UUID,
backend/app/api/v1/endpoints/claims.py:181:    """Add activity to a claim."""
backend/app/api/v1/endpoints/claims.py:183:    claim = service.get_claim(claim_id)
backend/app/api/v1/endpoints/claims.py:184:    if not claim or claim.company_id != current_user.company_id:
backend/app/api/v1/endpoints/claims.py:188:        claim_id=claim_id,
backend/app/api/v1/endpoints/documents.py:17:from app.models.document import Document, DocumentLabel
backend/app/api/v1/endpoints/documents.py:21:from app.services.document_service import document_service
backend/app/api/v1/endpoints/documents.py:56:    """Helper to format document for frontend with safety checks."""
backend/app/api/v1/endpoints/documents.py:116:        logger.error(f"FATAL error formatting document {getattr(doc, 'id', 'unknown')}: {str(e)}")
backend/app/api/v1/endpoints/documents.py:119:            "name": "Error loading document",
backend/app/api/v1/endpoints/documents.py:129:async def upload_document(
backend/app/api/v1/endpoints/documents.py:167:            "document": format_doc(new_doc, "Me"),
backend/app/api/v1/endpoints/documents.py:175:async def list_documents(
backend/app/api/v1/endpoints/documents.py:187:        # We need to eager load document and from_company to avoid late session issues
backend/app/api/v1/endpoints/documents.py:194:            if share.document:
backend/app/api/v1/endpoints/documents.py:196:                    "doc": share.document,
backend/app/api/v1/endpoints/documents.py:234:        logger.exception("Failed to list documents")
backend/app/api/v1/endpoints/documents.py:235:        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")
backend/app/api/v1/endpoints/documents.py:261:def list_policy_documents(
backend/app/api/v1/endpoints/documents.py:266:    """List auto-generated insurance documents for a specific policy."""
backend/app/api/v1/endpoints/documents.py:292:def get_policy_document(
backend/app/api/v1/endpoints/documents.py:298:    """Serve a specific auto-generated document."""
backend/app/api/v1/endpoints/documents.py:316:    file_path = os.path.join(str(document_service.output_dir), str(policy_id), safe_filename)
backend/app/api/v1/endpoints/documents.py:325:def generate_policy_documents(
backend/app/api/v1/endpoints/documents.py:331:    Trigger document generation for a policy (insurance certificate, insurance card, etc.).
backend/app/api/v1/endpoints/documents.py:336:        raise HTTPException(status_code=403, detail="Not authorized to generate documents")
backend/app/api/v1/endpoints/documents.py:356:        generated_paths = document_service.generate_documents(db, policy, client, company)
backend/app/api/v1/endpoints/documents.py:365:        "message": f"{len(generated_paths)} document(s) generated successfully.",
backend/app/api/v1/endpoints/employees.py:94:            payment_method=employee_in.profile.payment_method,
backend/app/api/v1/endpoints/employees.py:170:                payment_method=employee_in.profile.payment_method or "bank_transfer",
backend/app/api/v1/endpoints/employees.py:185:            if employee_in.profile.payment_method is not None:
backend/app/api/v1/endpoints/employees.py:186:                profile.payment_method = employee_in.profile.payment_method
backend/app/api/v1/endpoints/financial_reports.py:12:from app.repositories.payment_repository import PaymentRepository
backend/app/api/v1/endpoints/financial_reports.py:13:from app.repositories.premium_schedule_repository import PremiumScheduleRepository
backend/app/api/v1/endpoints/financial_reports.py:26:    payment_repo = PaymentRepository(db)
backend/app/api/v1/endpoints/financial_reports.py:34:    summary = payment_repo.get_revenue_summary(
backend/app/api/v1/endpoints/financial_reports.py:54:    payment_repo = PaymentRepository(db)
backend/app/api/v1/endpoints/financial_reports.py:64:        summary = payment_repo.get_revenue_summary(
backend/app/api/v1/endpoints/financial_reports.py:73:            "payments_count": summary['total_payments']
backend/app/api/v1/endpoints/financial_reports.py:91:    payment_repo = PaymentRepository(db)
backend/app/api/v1/endpoints/financial_reports.py:106:        summary = payment_repo.get_revenue_summary(
backend/app/api/v1/endpoints/financial_reports.py:115:            "payments_count": summary['total_payments']
backend/app/api/v1/endpoints/financial_reports.py:130:    schedule_repo = PremiumScheduleRepository(db)
backend/app/api/v1/endpoints/financial_reports.py:132:    # Get all overdue schedules
backend/app/api/v1/endpoints/financial_reports.py:133:    overdue = schedule_repo.get_overdue(current_user.company_id)
backend/app/api/v1/endpoints/financial_reports.py:136:    upcoming = schedule_repo.get_upcoming_due(current_user.company_id, days=7)
backend/app/api/v1/endpoints/financial_reports.py:154:@router.get("/payments/breakdown")
backend/app/api/v1/endpoints/financial_reports.py:155:def get_payment_breakdown(
backend/app/api/v1/endpoints/financial_reports.py:161:    """Get payment breakdown by method."""
backend/app/api/v1/endpoints/financial_reports.py:162:    payment_repo = PaymentRepository(db)
backend/app/api/v1/endpoints/financial_reports.py:170:    breakdown = payment_repo.get_payment_breakdown(
backend/app/api/v1/endpoints/financial_reports.py:189:    payment_repo = PaymentRepository(db)
backend/app/api/v1/endpoints/financial_reports.py:190:    schedule_repo = PremiumScheduleRepository(db)
backend/app/api/v1/endpoints/financial_reports.py:196:    monthly_revenue = payment_repo.get_revenue_summary(
backend/app/api/v1/endpoints/financial_reports.py:203:    today_revenue = payment_repo.get_revenue_summary(
backend/app/api/v1/endpoints/financial_reports.py:210:    overdue = schedule_repo.get_overdue(current_user.company_id)
backend/app/api/v1/endpoints/financial_reports.py:211:    upcoming = schedule_repo.get_upcoming_due(current_user.company_id, days=7)
backend/app/api/v1/endpoints/financial_reports.py:217:    payment_breakdown = payment_repo.get_payment_breakdown(
backend/app/api/v1/endpoints/financial_reports.py:226:            "payments_count": today_revenue['total_payments']
backend/app/api/v1/endpoints/financial_reports.py:230:            "payments_count": monthly_revenue['total_payments']
backend/app/api/v1/endpoints/financial_reports.py:238:        "payment_methods": payment_breakdown
backend/app/api/v1/endpoints/import_export.py:164:        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
backend/app/api/v1/endpoints/kyc.py:33:@router.post("/parse-document")
backend/app/api/v1/endpoints/kyc.py:34:async def parse_document(
backend/app/api/v1/endpoints/kyc.py:36:    doc_type: str = Body("identity_document", embed=True),
backend/app/api/v1/endpoints/kyc.py:41:    Parses a document image using AI and returns extracted fields.
backend/app/api/v1/endpoints/kyc.py:46:    results = await ai_service.parse_kyc_document(image_url, doc_type, company_id=company_id)
backend/app/api/v1/endpoints/kyc.py:56:    doc_type: str = Form("identity_document"),
backend/app/api/v1/endpoints/kyc.py:82:    # For simplicity, we'll pass the local path to a new service method or update parse_kyc_document.
backend/app/api/v1/endpoints/kyc.py:91:    results = await ai_service.parse_kyc_document_bytes(image_data, doc_type, company_id=company_id)
backend/app/api/v1/endpoints/kyc.py:108:                auto.registration_document_url = relative_path
backend/app/api/v1/endpoints/kyc.py:110:            elif doc_type == "identity_document":
backend/app/api/v1/endpoints/ml_models.py:39:@router.post("/predict/fraud/{claim_id}")
backend/app/api/v1/endpoints/ml_models.py:41:    claim_id: UUID,
backend/app/api/v1/endpoints/ml_models.py:46:    Predict fraud risk for a claim.
backend/app/api/v1/endpoints/ml_models.py:49:    return service.predict_fraud(claim_id)
backend/app/api/v1/endpoints/notifications.py:12:from app.models.notification import Notification
backend/app/api/v1/endpoints/notifications.py:18:async def get_notifications(
backend/app/api/v1/endpoints/notifications.py:27:    Get notifications.
backend/app/api/v1/endpoints/notifications.py:29:    scope='all': all company notifications (Admin only).
backend/app/api/v1/endpoints/notifications.py:37:            raise HTTPException(status_code=403, detail="Not authorized to view all notifications")
backend/app/api/v1/endpoints/notifications.py:43:    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
backend/app/api/v1/endpoints/notifications.py:48:            "type": n.notification_type,
backend/app/api/v1/endpoints/notifications.py:54:            "metadata": n.notification_metadata or {}
backend/app/api/v1/endpoints/notifications.py:56:        for n in notifications
backend/app/api/v1/endpoints/notifications.py:59:@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
backend/app/api/v1/endpoints/notifications.py:60:async def mark_notification_read(
backend/app/api/v1/endpoints/notifications.py:61:    notification_id: UUID,
backend/app/api/v1/endpoints/notifications.py:65:    """Mark a notification as read."""
backend/app/api/v1/endpoints/notifications.py:66:    notification = db.query(Notification).filter(
backend/app/api/v1/endpoints/notifications.py:67:        Notification.id == notification_id,
backend/app/api/v1/endpoints/notifications.py:71:    if not notification:
backend/app/api/v1/endpoints/notifications.py:74:    notification.status = 'read'
backend/app/api/v1/endpoints/notifications.py:76:    notification.read_at = utcnow()
backend/app/api/v1/endpoints/ocr.py:18:async def process_document(
backend/app/api/v1/endpoints/ocr.py:19:    document: UploadFile = File(...),
backend/app/api/v1/endpoints/ocr.py:20:    document_type: Optional[str] = None,
backend/app/api/v1/endpoints/ocr.py:24:    """Process an uploaded document with OCR/AI."""
backend/app/api/v1/endpoints/ocr.py:25:    if not document:
backend/app/api/v1/endpoints/ocr.py:28:    image_bytes = await document.read()
backend/app/api/v1/endpoints/ocr.py:30:    record = await service.process_document(
backend/app/api/v1/endpoints/ocr.py:33:        document_type=document_type,
backend/app/api/v1/endpoints/ocr.py:38:@router.get("/results/{document_id}", response_model=OCRProcessResponse)
backend/app/api/v1/endpoints/ocr.py:40:    document_id: str,
backend/app/api/v1/endpoints/ocr.py:44:    """Get OCR results by document_id."""
backend/app/api/v1/endpoints/ocr.py:46:    result = service.get_result(document_id)
backend/app/api/v1/endpoints/ocr.py:61:        document_id=payload.document_id,
backend/app/api/v1/endpoints/payments.py:2:API endpoints for payments.
backend/app/api/v1/endpoints/payments.py:12:from app.schemas.payment import (
