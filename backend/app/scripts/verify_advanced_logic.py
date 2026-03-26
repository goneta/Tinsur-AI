"""
Verification script for Phase 7 Advanced Logic.
"""
import sys
import os
import uuid
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.payment import Payment
from app.models.telematics import TelematicsData
from app.models.loyalty import LoyaltyPoint
from app.models.ticket import Ticket

from app.services.ml_service import MLService
from app.services.telematics_service import TelematicsService
from app.services.loyalty_service import LoyaltyService
from app.services.quote_service import QuoteService
from app.repositories.quote_repository import QuoteRepository

def verify_advanced_logic():
    db = SessionLocal()
    try:
        print("--- Starting Advanced Logic Verification ---")
        
        # 1. Setup Data
        company = db.query(Company).first()
        if not company:
            print("Error: No company found.")
            return

        user = db.query(User).filter(User.company_id == company.id).first()
        
        client = db.query(Client).filter(Client.company_id == company.id).first()
        if not client:
             client = Client(
                 company_id=company.id,
                 client_type="individual",
                 first_name="Advanced",
                 last_name="Tester",
                 email="adv@test.com",
                 user_id=user.id
             )
             db.add(client)
             db.commit()
             db.refresh(client)

        policy = db.query(Policy).filter(Policy.client_id == client.id).first()
        if not policy:
             from app.models.policy_type import PolicyType
             pt = db.query(PolicyType).filter(PolicyType.company_id == company.id).first()
             policy = Policy(
                 company_id=company.id,
                 client_id=client.id,
                 policy_type_id=pt.id,
                 policy_number=f"ADV-POL-{uuid.uuid4().hex[:6]}",
                 coverage_amount=Decimal('10000000'),
                 premium_amount=Decimal('500000'),
                 start_date=date.today(),
                 end_date=date.today() + timedelta(days=365),
                 status='active',
                 created_by=user.id
             )
             db.add(policy)
             db.commit()
             db.refresh(policy)

        print(f"Testing for Client: {client.display_name}, Policy: {policy.policy_number}")

        # 2. Verify ML Churn Prediction
        print("\n[ML Service] Testing Churn Prediction...")
        # Add some delay factors
        ticket = Ticket(
            company_id=company.id,
            client_id=client.id,
            ticket_number=f"T-RET-{uuid.uuid4().hex[:6].upper()}",
            subject="Late payment issue",
            description="I am struggling to pay",
            status="open",
            priority="high",
            category="billing"
        )
        db.add(ticket)
        db.commit()
        
        ml_service = MLService(db)
        churn_pred = ml_service.predict_churn(client.id)
        print(f"Churn Score: {churn_pred['score']}, Risk: {churn_pred['risk_level']}")
        print(f"Recommendations: {churn_pred['recommendations']}")

        # 3. Verify Telematics & UBI
        print("\n[Telematics Service] Testing Trip Submission & UBI Adjustment...")
        tele_service = TelematicsService(db)
        
        # Submit a "safe" trip
        safe_trip = {
            "distance_km": 15.5,
            "avg_speed": 45,
            "max_speed": 60,
            "harsh_braking_count": 0,
            "harsh_acceleration_count": 0,
            "night_driving_km": 0
        }
        tele_service.process_trip_data(policy.id, safe_trip)
        
        # Submit a "risky" trip
        risky_trip = {
            "distance_km": 50.0,
            "avg_speed": 115,
            "max_speed": 140,
            "harsh_braking_count": 5,
            "harsh_acceleration_count": 3,
            "night_driving_km": 20
        }
        tele_service.process_trip_data(policy.id, risky_trip)
        
        score = tele_service.calculate_safety_score(policy.id)
        adjustment = tele_service.get_ubi_adjustment(policy.id)
        print(f"Safety Score: {score}, UBI Adjustment: {float(adjustment * 100)}%")

        # 4. Verify Quote UBI Integration
        print("\n[Quote Service] Testing UBI Integration in Pricing...")
        quote_repo = QuoteRepository(db)
        quote_service = QuoteService(quote_repo)
        
        calc = quote_service.calculate_premium(
            policy_type_id=policy.policy_type_id,
            coverage_amount=policy.coverage_amount,
            risk_factors=policy.details or {},
            policy_id=policy.id
        )
        print(f"Base Premium: {calc['base_premium']}")
        print(f"UBI Adjustment amount: {calc['ubi_adjustment']}")
        print(f"Final Premium: {calc['final_premium']}")

        # 5. Verify Loyalty Points
        print("\n[Loyalty Service] Testing Point Earning & Tiers...")
        loyalty_service = LoyaltyService(db)
        
        # Award points for a large payment
        points_record = loyalty_service.award_points(client.id, Decimal('5000000'), "Large premium payment")
        print(f"Points Balance: {points_record.points_balance}, Tier: {points_record.tier}")
        
        # Redeem some points
        discount = loyalty_service.redeem_points(client.id, 500)
        print(f"Redeemed 500 points for {discount} XOF discount.")
        print(f"Remaining Balance: {points_record.points_balance}")

        print("\n--- Advanced Logic Verification Successful ---")

    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_advanced_logic()
