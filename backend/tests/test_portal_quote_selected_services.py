from app.core.security import get_password_hash
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy_service import PolicyService
from app.models.premium_policy import PremiumPolicyType


def test_portal_quote_selected_services_affect_premium(client, db_session):
    # Setup company
    company = Company(
        name="Test Insurance Co",
        subdomain="test",
        email="test@insurance.com",
        phone="+225 27 20 00 00 00"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)

    # Setup client user
    user = User(
        company_id=company.id,
        email="client@test.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Client",
        last_name="User",
        role="client",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Setup client record linked to user
    client_record = Client(
        user_id=user.id,
        client_type="individual",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    db_session.add(client_record)
    db_session.commit()
    db_session.refresh(client_record)

    # Link client to company (association table)
    client_record.companies = [company]
    db_session.add(client_record)
    db_session.commit()

    # Setup services
    included_service = PolicyService(
        company_id=company.id,
        name_en="Included Service",
        default_price=0
    )
    optional_service = PolicyService(
        company_id=company.id,
        name_en="Optional Service",
        default_price=10
    )
    db_session.add(included_service)
    db_session.add(optional_service)
    db_session.commit()

    # Setup premium policy type with included service
    policy_type = PremiumPolicyType(
        company_id=company.id,
        name="Bronze Cover",
        price=100,
        excess=0,
        is_active=True
    )
    policy_type.services = [included_service]
    db_session.add(policy_type)
    db_session.commit()
    db_session.refresh(policy_type)

    # Login as client
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "client@test.com", "password": "testpass123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Calculate without optional services
    base_resp = client.post(
        "/api/v1/portal/quotes/calculate",
        headers=headers,
        json={
            "client_id": str(client_record.id),
            "policy_type_id": str(policy_type.id),
            "coverage_amount": 1000,
            "premium_frequency": "annual",
            "duration_months": 12,
            "risk_factors": {},
            "selected_services": []
        }
    )
    assert base_resp.status_code == 200
    base_data = base_resp.json()

    # Calculate with optional service selected
    opt_resp = client.post(
        "/api/v1/portal/quotes/calculate",
        headers=headers,
        json={
            "client_id": str(client_record.id),
            "policy_type_id": str(policy_type.id),
            "coverage_amount": 1000,
            "premium_frequency": "annual",
            "duration_months": 12,
            "risk_factors": {},
            "selected_services": [str(optional_service.id)]
        }
    )
    assert opt_resp.status_code == 200
    opt_data = opt_resp.json()

    # Optional service should increase extra fee and final premium
    assert float(opt_data["extra_fee"]) >= 10
    assert float(opt_data["final_premium"]) > float(base_data["final_premium"])
