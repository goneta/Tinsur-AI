"""
Underwriting service for managing authority and referrals.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from app.core.time import utcnow

from app.models.underwriting import UnderwritingReferral
from app.models.user import User
from app.models.quote import Quote

class UnderwritingService:
    def __init__(self, db: Session):
        self.db = db

    def is_within_authority(self, user_id: UUID, coverage_amount: Decimal) -> bool:
        """
        Check if the coverage amount is within the user's underwriting authority.
        Super admins and company admins are assumed to have unlimited authority 
        unless specific limits are set.
        """
        user = self.db.query(User).get(user_id)
        if not user:
            return False
            
        if user.role in ['super_admin', 'company_admin']:
            return True
            
        return coverage_amount <= user.underwriting_limit

    def create_referral(
        self, 
        referred_by_id: UUID, 
        reason: str,
        quote_id: Optional[UUID] = None, 
        endorsement_id: Optional[UUID] = None
    ) -> UnderwritingReferral:
        """
        Create a new underwriting referral for a quote or endorsement.
        """
        if not quote_id and not endorsement_id:
            raise ValueError("Either quote_id or endorsement_id must be provided")
            
        company_id = None
        if quote_id:
            from app.models.quote import Quote
            quote = self.db.query(Quote).get(quote_id)
            if not quote:
                raise ValueError("Quote not found")
            company_id = quote.company_id
            quote.status = 'referred'
        elif endorsement_id:
            from app.models.endorsement import Endorsement
            endorsement = self.db.query(Endorsement).get(endorsement_id)
            if not endorsement:
                raise ValueError("Endorsement not found")
            company_id = endorsement.company_id
            endorsement.status = 'pending_approval'
            
        referral = UnderwritingReferral(
            company_id=company_id,
            quote_id=quote_id,
            endorsement_id=endorsement_id,
            referred_by_id=referred_by_id,
            reason=reason,
            status='pending'
        )
        self.db.add(referral)
        self.db.commit()
        return referral

    def process_referral_decision(self, referral_id: UUID, decided_by_id: UUID, status: str, notes: str) -> Optional[Any]:
        """
        Process a decision on an underwriting referral.
        Status must be 'approved' or 'rejected'.
        """
        if status not in ['approved', 'rejected']:
            raise ValueError("Invalid status. Must be 'approved' or 'rejected'.")
            
        referral = self.db.query(UnderwritingReferral).get(referral_id)
        if not referral:
            raise ValueError("Referral not found")
            
        referral.status = status
        referral.decision_notes = notes
        referral.decided_by_id = decided_by_id
        referral.decided_at = utcnow()
        
        result = None
        # Update quote status
        if referral.quote_id:
            quote = self.db.query(Quote).get(referral.quote_id)
            if quote:
                if status == 'approved':
                    quote.status = 'accepted'
                else:
                    quote.status = 'rejected'
                result = quote
        
        # Update endorsement status
        elif referral.endorsement_id:
            from app.models.endorsement import Endorsement
            endorsement = self.db.query(Endorsement).get(referral.endorsement_id)
            if endorsement:
                if status == 'approved':
                    endorsement.status = 'approved'
                    endorsement.approved_by = decided_by_id
                    endorsement.approved_at = utcnow()
                else:
                    endorsement.status = 'rejected'
                    endorsement.rejection_reason = notes
                result = endorsement
            
        self.db.commit()
        return result

    def get_pending_referrals(self, company_id: UUID) -> List[UnderwritingReferral]:
        """Get all pending referrals for a company."""
        return self.db.query(UnderwritingReferral).options(
            joinedload(UnderwritingReferral.quote).joinedload(Quote.client),
            joinedload(UnderwritingReferral.referrer)
        ).filter(
            UnderwritingReferral.company_id == company_id,
            UnderwritingReferral.status == 'pending'
        ).all()

    def _decimal_money(self, value: Any) -> Decimal:
        """Convert values to a two-decimal Decimal for deterministic money calculations."""
        return Decimal(str(value or 0)).quantize(Decimal("0.01"))

    def _age_on_today(self, birth_date: Any) -> int:
        today = datetime.utcnow().date()
        if isinstance(birth_date, str):
            birth_date = datetime.fromisoformat(birth_date).date()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def _latest_active_rule_set(self, company_id: UUID):
        from app.models.underwriting import UnderwritingRuleSet
        return self.db.query(UnderwritingRuleSet).filter(
            UnderwritingRuleSet.company_id == company_id,
            UnderwritingRuleSet.status == "active"
        ).order_by(UnderwritingRuleSet.effective_from.desc().nullslast(), UnderwritingRuleSet.created_at.desc()).first()

    def deterministic_quote_underwriting(
        self,
        *,
        company_id: UUID,
        intake: Dict[str, Any],
        quote_id: Optional[UUID] = None,
        created_by_id: Optional[UUID] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        """
        Accept a normalized automobile quote intake payload and return a deterministic
        accept/refer/decline underwriting decision. When `persist` is true, the service
        stores the normalized vehicle, driver, decision, and quote snapshot records.
        """
        from app.models.underwriting import (
            Driver,
            DriverClaimHistory,
            DriverConvictionHistory,
            QuoteUnderwritingSnapshot,
            UnderwritingDecision,
            Vehicle,
            VehicleRiskProfile,
        )

        client = intake["client"]
        vehicle_data = intake["vehicle"]
        drivers_data = intake["drivers"]
        usage = intake.get("usage") or {}
        cover_options = intake["cover_options"]
        ncd = intake.get("ncd") or {}
        payment_terms = intake.get("payment_terms") or {}

        referral_reasons: List[Dict[str, Any]] = []
        decline_reasons: List[Dict[str, Any]] = []
        required_documents: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        assumptions: List[str] = []
        rule_matches: List[Dict[str, Any]] = []

        coverage_amount = self._decimal_money(cover_options.get("coverage_amount", 0))
        vehicle_value = self._decimal_money(vehicle_data.get("market_value", 0))
        current_year = datetime.utcnow().year
        vehicle_age = max(0, current_year - int(vehicle_data.get("year") or current_year))
        usage_class = (usage.get("use_class") or vehicle_data.get("usage_class") or "private").lower()
        annual_mileage = int(vehicle_data.get("annual_mileage") or 0)

        rule_set = self._latest_active_rule_set(company_id)
        base_rate = Decimal(str(getattr(rule_set, "default_base_rate", None) or "0.045"))
        base_premium = (coverage_amount * base_rate).quantize(Decimal("0.01"))

        factors: Dict[str, Decimal] = {
            "vehicle": Decimal("1.00"),
            "driver": Decimal("1.00"),
            "usage": Decimal("1.00"),
            "location": Decimal("1.00"),
            "claims_convictions": Decimal("1.00"),
            "ncd": Decimal("1.00"),
            "payment": Decimal("1.00"),
        }
        risk_score = Decimal("20.00")

        if vehicle_age > 20:
            referral_reasons.append({"code": "vehicle_age_referral", "message": "Vehicle is older than 20 years and requires manual underwriting review."})
            required_documents.append({"code": "inspection_report", "message": "Vehicle inspection report required."})
            rule_matches.append({"code": "VEHICLE_AGE_GT_20", "effect": "refer"})
            factors["vehicle"] += Decimal("0.25")
            risk_score += Decimal("18")
        elif vehicle_age > 12:
            factors["vehicle"] += Decimal("0.12")
            risk_score += Decimal("8")
            rule_matches.append({"code": "VEHICLE_AGE_GT_12", "effect": "rate"})

        if vehicle_value > Decimal("150000"):
            referral_reasons.append({"code": "high_value_vehicle", "message": "Vehicle value exceeds automatic underwriting limit."})
            required_documents.append({"code": "purchase_invoice", "message": "Proof of vehicle value required."})
            factors["vehicle"] += Decimal("0.20")
            risk_score += Decimal("15")
            rule_matches.append({"code": "VEHICLE_VALUE_GT_150000", "effect": "refer"})

        if vehicle_data.get("modifications"):
            referral_reasons.append({"code": "vehicle_modifications", "message": "Declared modifications require manual review."})
            required_documents.append({"code": "modification_declaration", "message": "Modification details and receipts required."})
            factors["vehicle"] += Decimal("0.10")
            risk_score += Decimal("10")
            rule_matches.append({"code": "MODIFICATIONS_PRESENT", "effect": "refer"})

        if vehicle_data.get("imported"):
            referral_reasons.append({"code": "imported_vehicle", "message": "Imported vehicles require manual validation."})
            factors["vehicle"] += Decimal("0.08")
            risk_score += Decimal("6")
            rule_matches.append({"code": "IMPORTED_VEHICLE", "effect": "refer"})

        prohibited_usage = {"taxi", "courier", "delivery", "rideshare"}
        if usage_class in prohibited_usage or usage.get("delivery_or_rideshare"):
            referral_reasons.append({"code": "commercial_usage_review", "message": "Commercial, taxi, delivery, or rideshare use requires underwriter review."})
            factors["usage"] += Decimal("0.35")
            risk_score += Decimal("20")
            rule_matches.append({"code": "COMMERCIAL_USAGE", "effect": "refer"})
        elif usage.get("business_use"):
            factors["usage"] += Decimal("0.12")
            risk_score += Decimal("6")
            rule_matches.append({"code": "BUSINESS_USE", "effect": "rate"})

        if annual_mileage > 30000:
            referral_reasons.append({"code": "high_mileage", "message": "Annual mileage exceeds automatic threshold."})
            factors["usage"] += Decimal("0.18")
            risk_score += Decimal("10")
            rule_matches.append({"code": "MILEAGE_GT_30000", "effect": "refer"})
        elif annual_mileage > 18000:
            factors["usage"] += Decimal("0.08")
            risk_score += Decimal("5")
            rule_matches.append({"code": "MILEAGE_GT_18000", "effect": "rate"})

        primary_driver = next((driver for driver in drivers_data if driver.get("is_primary")), drivers_data[0])
        min_driver_age = 120
        total_claims = 0
        total_conviction_points = 0
        for driver in drivers_data:
            driver_age = self._age_on_today(driver["date_of_birth"])
            min_driver_age = min(min_driver_age, driver_age)
            claims = driver.get("claims_history") or []
            convictions = driver.get("conviction_history") or []
            total_claims += len(claims)
            total_conviction_points += sum(int(conviction.get("points") or 0) for conviction in convictions)

            if driver_age < 18:
                decline_reasons.append({"code": "driver_under_minimum_age", "message": "At least one driver is below the minimum insurable age."})
                rule_matches.append({"code": "DRIVER_AGE_LT_18", "effect": "decline"})
            elif driver_age < 25:
                factors["driver"] += Decimal("0.25")
                risk_score += Decimal("15")
                rule_matches.append({"code": "YOUNG_DRIVER_LT_25", "effect": "rate"})

            if int(driver.get("years_licensed") or 0) < 1:
                referral_reasons.append({"code": "newly_licensed_driver", "message": "Driver licensed for less than one year requires review."})
                factors["driver"] += Decimal("0.15")
                risk_score += Decimal("8")
                rule_matches.append({"code": "LICENSE_YEARS_LT_1", "effect": "refer"})

            if driver.get("cancellation_or_refusal_history"):
                referral_reasons.append({"code": "prior_cancellation_or_refusal", "message": "Previous cancellation or refusal requires manual review."})
                risk_score += Decimal("14")
                rule_matches.append({"code": "PRIOR_REFUSAL", "effect": "refer"})

            severe_convictions = [conviction for conviction in convictions if str(conviction.get("severity", "")).lower() in {"major", "severe"}]
            if severe_convictions:
                referral_reasons.append({"code": "major_conviction", "message": "Major conviction requires underwriting review."})
                factors["claims_convictions"] += Decimal("0.25")
                risk_score += Decimal("20")
                rule_matches.append({"code": "MAJOR_CONVICTION", "effect": "refer"})

        if total_claims > 3:
            referral_reasons.append({"code": "excessive_claims_history", "message": "More than three claim records require underwriter review."})
            factors["claims_convictions"] += Decimal("0.30")
            risk_score += Decimal("18")
            rule_matches.append({"code": "CLAIMS_GT_3", "effect": "refer"})
        elif total_claims:
            factors["claims_convictions"] += Decimal("0.08") * Decimal(str(total_claims))
            risk_score += Decimal("5") * Decimal(str(total_claims))
            rule_matches.append({"code": "CLAIMS_PRESENT", "effect": "rate", "count": total_claims})

        if total_conviction_points >= 12:
            referral_reasons.append({"code": "high_conviction_points", "message": "Conviction points exceed automatic threshold."})
            factors["claims_convictions"] += Decimal("0.25")
            risk_score += Decimal("16")
            rule_matches.append({"code": "CONVICTION_POINTS_GTE_12", "effect": "refer"})
        elif total_conviction_points:
            factors["claims_convictions"] += Decimal("0.02") * Decimal(str(total_conviction_points))
            risk_score += Decimal(str(total_conviction_points))
            rule_matches.append({"code": "CONVICTION_POINTS_PRESENT", "effect": "rate", "points": total_conviction_points})

        ncd_years = max(int(ncd.get("years") or primary_driver.get("no_claim_discount_years") or 0), 0)
        ncd_discount = min(Decimal(str(ncd_years)) * Decimal("0.04"), Decimal("0.30"))
        factors["ncd"] -= ncd_discount
        if ncd_years > 0 and not ncd.get("proof_available"):
            required_documents.append({"code": "ncd_proof", "message": "Proof of no-claim discount required before policy issuance."})
            warnings.append({"code": "ncd_unverified", "message": "No-claim discount was applied but proof is not yet verified."})
            rule_matches.append({"code": "NCD_PROOF_REQUIRED", "effect": "document"})

        if payment_terms.get("premium_frequency") == "monthly" or payment_terms.get("finance_requested"):
            factors["payment"] += Decimal("0.06")
            rule_matches.append({"code": "MONTHLY_OR_FINANCED_PAYMENT", "effect": "rate"})

        if not client.get("consent_to_underwrite", True):
            decline_reasons.append({"code": "missing_underwriting_consent", "message": "The client has not consented to underwriting checks."})
            rule_matches.append({"code": "CONSENT_REQUIRED", "effect": "decline"})

        combined_factor = Decimal("1.00")
        for factor in factors.values():
            combined_factor *= factor
        final_premium = (base_premium * combined_factor).quantize(Decimal("0.01"))
        risk_score = max(Decimal("0.00"), min(risk_score, Decimal("100.00"))).quantize(Decimal("0.01"))

        decision = "accept"
        if decline_reasons:
            decision = "decline"
        elif referral_reasons:
            decision = "refer"

        breakdown = {
            "coverage_amount": str(coverage_amount),
            "base_rate": str(base_rate),
            "base_premium": str(base_premium),
            "vehicle_factor": str(factors["vehicle"].quantize(Decimal("0.0001"))),
            "driver_factor": str(factors["driver"].quantize(Decimal("0.0001"))),
            "usage_factor": str(factors["usage"].quantize(Decimal("0.0001"))),
            "location_factor": str(factors["location"].quantize(Decimal("0.0001"))),
            "claims_convictions_factor": str(factors["claims_convictions"].quantize(Decimal("0.0001"))),
            "ncd_factor": str(factors["ncd"].quantize(Decimal("0.0001"))),
            "payment_factor": str(factors["payment"].quantize(Decimal("0.0001"))),
            "combined_factor": str(combined_factor.quantize(Decimal("0.0001"))),
            "final_premium": str(final_premium),
        }

        normalized_payload = {
            "client": client,
            "vehicle": vehicle_data,
            "drivers": drivers_data,
            "usage": usage,
            "cover_options": cover_options,
            "ncd": ncd,
            "payment_terms": payment_terms,
        }
        if not assumptions:
            assumptions.append("Default deterministic automobile rule set applied where no active company-specific rule set exists.")

        result = {
            "decision": decision,
            "quote_id": quote_id,
            "underwriting_decision_id": None,
            "snapshot_id": None,
            "rule_version_id": getattr(rule_set, "id", None),
            "base_premium": base_premium,
            "final_premium": final_premium,
            "risk_score": risk_score,
            "breakdown": breakdown,
            "referral_reasons": referral_reasons,
            "decline_reasons": decline_reasons,
            "required_documents": required_documents,
            "warnings": warnings,
            "assumptions": assumptions,
            "rule_matches": rule_matches,
            "normalized_payload": normalized_payload,
            "created_at": utcnow(),
        }

        if not persist:
            return result

        vehicle = Vehicle(
            company_id=company_id,
            client_id=client["client_id"],
            client_automobile_id=vehicle_data.get("client_automobile_id"),
            registration_number=vehicle_data.get("registration_number"),
            vin=vehicle_data.get("vin"),
            make=vehicle_data["make"],
            model=vehicle_data["model"],
            variant=vehicle_data.get("variant"),
            year=vehicle_data["year"],
            body_type=vehicle_data.get("body_type"),
            fuel_type=vehicle_data.get("fuel_type"),
            transmission=vehicle_data.get("transmission"),
            engine_size_cc=vehicle_data.get("engine_size_cc"),
            seat_count=vehicle_data.get("seat_count"),
            market_value=vehicle_value,
            annual_mileage=vehicle_data.get("annual_mileage"),
            usage_class=vehicle_data.get("usage_class") or usage_class,
            garaging_postcode=vehicle_data.get("garaging_postcode"),
            garaging_region=vehicle_data.get("garaging_region"),
            overnight_parking=vehicle_data.get("overnight_parking"),
            security_devices=vehicle_data.get("security_devices") or [],
            modifications=vehicle_data.get("modifications") or [],
            imported=vehicle_data.get("imported", False),
            prior_damage=vehicle_data.get("prior_damage", False),
        )
        self.db.add(vehicle)
        self.db.flush()

        risk_profile = VehicleRiskProfile(
            company_id=company_id,
            vehicle_id=vehicle.id,
            risk_group="high" if risk_score >= Decimal("70") else "referred" if decision == "refer" else "standard",
            risk_score=risk_score,
            factors={key: str(value) for key, value in factors.items()},
            reason_codes=[match["code"] for match in rule_matches],
        )
        self.db.add(risk_profile)

        for driver_data in drivers_data:
            driver = Driver(
                company_id=company_id,
                client_id=client["client_id"],
                vehicle_id=vehicle.id,
                client_driver_id=driver_data.get("client_driver_id"),
                is_primary=driver_data.get("is_primary", False),
                first_name=driver_data["first_name"],
                last_name=driver_data["last_name"],
                date_of_birth=driver_data["date_of_birth"],
                licence_type=driver_data.get("licence_type"),
                licence_issue_date=driver_data.get("licence_issue_date"),
                years_licensed=driver_data.get("years_licensed", 0),
                occupation=driver_data.get("occupation"),
                marital_status=driver_data.get("marital_status"),
                address_postcode=driver_data.get("address_postcode"),
                address_region=driver_data.get("address_region"),
                no_claim_discount_years=driver_data.get("no_claim_discount_years", 0),
                no_claim_discount_protected=driver_data.get("no_claim_discount_protected", False),
                previous_insurer=driver_data.get("previous_insurer"),
                cancellation_or_refusal_history=driver_data.get("cancellation_or_refusal_history", False),
                relationship_to_policyholder=driver_data.get("relationship_to_policyholder"),
            )
            self.db.add(driver)
            self.db.flush()
            for claim in driver_data.get("claims_history") or []:
                self.db.add(DriverClaimHistory(driver_id=driver.id, **claim))
            for conviction in driver_data.get("conviction_history") or []:
                self.db.add(DriverConvictionHistory(driver_id=driver.id, **conviction))

        decision_record = UnderwritingDecision(
            company_id=company_id,
            quote_id=quote_id,
            rule_set_id=getattr(rule_set, "id", None),
            decision=decision,
            base_premium=base_premium,
            final_premium=final_premium,
            risk_score=risk_score,
            breakdown=breakdown,
            referral_reasons=referral_reasons,
            decline_reasons=decline_reasons,
            required_documents=required_documents,
            warnings=warnings,
            assumptions=assumptions,
            rule_matches=rule_matches,
            input_snapshot=normalized_payload,
        )
        self.db.add(decision_record)
        self.db.flush()
        result["underwriting_decision_id"] = decision_record.id

        if quote_id:
            quote = self.db.query(Quote).get(quote_id)
            if quote:
                quote.premium_amount = base_premium
                quote.final_premium = final_premium
                quote.risk_score = risk_score
                quote.calculation_breakdown = breakdown
                quote.details = {**(quote.details or {}), "underwriting": normalized_payload}
                if decision == "decline":
                    quote.status = "rejected"
                elif decision == "refer":
                    quote.status = "under_review"

            snapshot = self.db.query(QuoteUnderwritingSnapshot).filter(
                QuoteUnderwritingSnapshot.quote_id == quote_id
            ).first()
            if not snapshot:
                snapshot = QuoteUnderwritingSnapshot(company_id=company_id, quote_id=quote_id)
                self.db.add(snapshot)
            snapshot.underwriting_decision_id = decision_record.id
            snapshot.rule_set_id = getattr(rule_set, "id", None)
            snapshot.normalized_payload = normalized_payload
            snapshot.decision_snapshot = {key: value for key, value in result.items() if key != "normalized_payload"}
            snapshot.premium_breakdown = breakdown
            snapshot.policy_ready_payload = {
                "client_id": str(client["client_id"]),
                "vehicle_id": str(vehicle.id),
                "decision_id": str(decision_record.id),
                "premium": str(final_premium),
                "decision": decision,
                "required_documents": required_documents,
            }
            snapshot.valid_until = datetime.utcnow() + timedelta(days=30)
            self.db.flush()
            result["snapshot_id"] = snapshot.id

        self.db.commit()
        return result
