### Acquisition schema line numbers
444:class ProductPolicyAcquisitionRequest(BaseModel):
458:class ProductPolicyAcquisitionResponse(BaseModel):
### Documents endpoint policy routes
128:@router.post("/upload")
174:@router.get("/list")
237:@router.post("/{doc_id}/share")
260:@router.get("/policy/{policy_id}", response_model=List[str])
261:def list_policy_documents(
291:@router.get("/policy/{policy_id}/{filename}")
292:def get_policy_document(
324:@router.post("/policy/{policy_id}/generate")
325:def generate_policy_documents(
331:    Trigger document generation for a policy (insurance certificate, insurance card, etc.).
### Document service methods
16:from app.models.policy import Policy
23:class DocumentService:
24:    def __init__(self):
34:    def _generate_qr_code(self, data: str) -> str:
49:    def _generate_qr_png_bytes(self, data: str) -> bytes:
63:    def _generate_verification_code(self) -> str:
67:    def _format_currency(self, amount: float, currency: str = "GBP") -> str:
71:    def _extract_placeholders(self, html_content: str) -> List[str]:
75:    def _build_data_mapping(
77:        policy: Policy,
95:            "numero_police": policy.policy_number,
96:            "date_debut": policy.start_date.strftime("%d/%m/%Y") if policy.start_date else "",
97:            "date_fin": policy.end_date.strftime("%d/%m/%Y") if policy.end_date else "",
98:            "prime_totale": self._format_currency(float(policy.premium_amount or 0)),
99:            "montant_couverture": self._format_currency(float(policy.coverage_amount or 0)),
100:            "type_assurance": policy.policy_type.name if policy.policy_type else "General",
107:    def _html_to_text(self, html_content: str) -> str:
117:    def _render_pdf(
147:    def _load_templates_from_files(self) -> List[Dict[str, Any]]:
166:    def _ensure_templates_loaded(self, db) -> None:
184:    def _get_policy_vehicle(self, policy: Policy, client: Client) -> dict:
185:        if policy.details and isinstance(policy.details, dict):
186:            vehicle = policy.details.get("vehicle") or {}
204:    def _generate_unique_code(self, db) -> str:
210:    def generate_documents(self, db, policy: Policy, client: Client, company: Company) -> List[str]:
212:        Generates all insurance documents for a given policy.
217:        policy_dir = self.output_dir / str(policy.id)
218:        policy_dir.mkdir(parents=True, exist_ok=True)
221:        vehicle = self._get_policy_vehicle(policy, client)
222:        data_mapping = self._build_data_mapping(policy, client, company, vehicle)
263:                "policy_number": policy.policy_number,
269:            output_filename = f"{template.code}_{policy.policy_number}.pdf"
270:            output_path = policy_dir / output_filename
273:            file_url = f"documents/{policy.id}/{output_filename}"
278:                policy_id=policy.id,
281:                uploaded_by=policy.created_by,
### Policy agent tool methods
11:def _get_backend_root():
19:def list_draft_quotes(company_id: str) -> str:
33:                joinedload(Quote.policy_type)
43:                "policy_type": q.policy_type.name if q.policy_type else "General",
58:def convert_quote_to_policy(quote_id: str, company_id: str, user_id: str, start_date: str = None) -> str:
60:    Converts an accepted quote into an active insurance policy.
62:    start_date: Optional policy start date in YYYY-MM-DD format. Defaults to today.
63:    Returns the new policy details.
69:        from app.models.policy import Policy
71:        from app.repositories.policy_repository import PolicyRepository
73:        from app.services.policy_service import PolicyService
97:            existing_policy = db.query(Policy).filter(Policy.quote_id == quote.id).first()
98:            if existing_policy:
101:                    "message": f"Quote {quote.quote_number} has already been converted to Policy {existing_policy.policy_number}.",
102:                    "policy": {
103:                        "policy_number": existing_policy.policy_number,
106:                        "coverage_amount": float(existing_policy.coverage_amount) if existing_policy.coverage_amount else 0,
107:                        "premium_amount": float(existing_policy.premium_amount) if existing_policy.premium_amount else 0,
108:                        "start_date": existing_policy.start_date.isoformat() if existing_policy.start_date else "",
109:                        "end_date": existing_policy.end_date.isoformat() if existing_policy.end_date else "",
110:                        "status": existing_policy.status,
118:                    policy_start = datetime.strptime(start_date, "%Y-%m-%d").date()
120:                    policy_start = datetime.now().date()
122:                policy_start = datetime.now().date()
124:            policy_service = PolicyService(
129:            new_policy = policy_service.create_from_quote(quote.id, policy_start, uuid.UUID(user_id))
133:                "message": f"Policy {new_policy.policy_number} created successfully from Quote {quote.quote_number}.",
134:                "policy": {
135:                    "policy_number": new_policy.policy_number,
138:                    "coverage_amount": float(new_policy.coverage_amount) if new_policy.coverage_amount else 0,
139:                    "premium_amount": float(new_policy.premium_amount) if new_policy.premium_amount else 0,
140:                    "start_date": new_policy.start_date.isoformat() if new_policy.start_date else "",
141:                    "end_date": new_policy.end_date.isoformat() if new_policy.end_date else "",
142:                    "status": new_policy.status,
153:def list_active_policies(company_id: str, client_id: str = None) -> str:
156:    Returns policy details including status, dates, and premium amounts.
161:        from app.models.policy import Policy
168:                joinedload(Policy.policy_type)
178:                "policy_number": p.policy_number,
180:                "policy_type": p.policy_type.name if p.policy_type else "General",
197:def get_policy_details(policy_number: str, company_id: str) -> str:
199:    Gets detailed information about a specific policy including its services and claims.
204:        from app.models.policy import Policy
209:            policy = db.query(Policy).options(
211:                joinedload(Policy.policy_type),
216:                Policy.policy_number == policy_number
219:            if not policy:
220:                return json.dumps({"status": "error", "message": f"Policy '{policy_number}' not found."})
226:            } for c in (policy.claims or [])]
231:            } for s in (policy.services or [])]
235:                "policy": {
236:                    "policy_number": policy.policy_number,
237:                    "client_name": f"{policy.client.first_name} {policy.client.last_name}" if policy.client else "Unknown",
238:                    "policy_type": policy.policy_type.name if policy.policy_type else "General",
239:                    "premium_amount": float(policy.premium_amount) if policy.premium_amount else 0,
240:                    "coverage_amount": float(policy.coverage_amount) if policy.coverage_amount else 0,
241:                    "start_date": policy.start_date.isoformat() if policy.start_date else "",
242:                    "end_date": policy.end_date.isoformat() if policy.end_date else "",
243:                    "status": policy.status,
244:                    "auto_renew": policy.auto_renew if hasattr(policy, 'auto_renew') else False,
245:                    "days_until_expiry": policy.days_until_expiry if hasattr(policy, 'days_until_expiry') else 0,
257:def cancel_policy(policy_number: str, company_id: str, reason: str) -> str:
259:    Cancels an active policy with a reason.
264:        from app.models.policy import Policy
268:            policy = db.query(Policy).filter(
270:                Policy.policy_number == policy_number
273:            if not policy:
274:                return json.dumps({"status": "error", "message": f"Policy '{policy_number}' not found."})
276:            if policy.status == 'cancelled':
277:                return json.dumps({"status": "error", "message": f"Policy {policy_number} is already cancelled."})
279:            policy.status = 'cancelled'
280:            if hasattr(policy, 'cancellation_reason'):
281:                policy.cancellation_reason = reason
286:                "message": f"Policy {policy_number} has been cancelled. Reason: {reason}"
### Payment service methods
22:class PaymentService:
25:    def __init__(self, db: Session, payment_repo: PaymentRepository):
31:    def generate_payment_number(self, company_id: UUID) -> str:
37:    def create_payment(
40:        policy_id: UUID,
52:            policy_id=policy_id,
65:    def process_payment(
116:                    # Standard policy payment logic
117:                    self._handle_successful_policy_payment(payment)
131:    def _process_credit_topup(self, payment: Payment):
156:    def _process_stripe_payment(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
180:    def _process_mobile_money_payment(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
202:    def _post_payment_to_ledger(self, payment: Payment):
216:            if payment.policy:
217:                description = f"Premium payment received for Policy {payment.policy.policy_number}"
243:    def _process_bank_transfer(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
252:    def _process_cash_payment(self, payment: Payment, details: Dict[str, Any]) -> Dict[str, Any]:
261:    def refund_payment(
280:    def  handle_webhook(
308:                self._handle_successful_policy_payment(payment)
315:    def _handle_successful_policy_payment(self, payment: Payment):
316:        """Run idempotent side effects for a successful policy payment."""
318:        if metadata.get('policy_payment_side_effects_completed'):
324:        payment.payment_metadata = {**metadata, 'policy_payment_side_effects_completed': True}
326:    def _generate_co_insurance_premium_shares(self, payment: Payment):
330:        # 1. Get co-insurance shares for the policy
331:        shares = db.query(CoInsuranceShare).filter(CoInsuranceShare.policy_id == payment.policy_id).all()
361:    def _generate_commissions(self, payment: Payment):
365:        # Get policy to find business source
366:        from app.repositories.policy_repository import PolicyRepository
367:        policy_repo = PolicyRepository(db)
368:        policy = policy_repo.get_by_id(payment.policy_id)
370:        if not policy:
378:        comm_service.calculate_and_create_commission(policy, payment.amount)
