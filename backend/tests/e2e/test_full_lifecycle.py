import pytest
import uuid
import os
from datetime import date, datetime, timedelta
from app.core.security import get_password_hash
from app.models.user import User
from app.models.client import Client
from app.models.employee import EmployeeProfile

def log_error(msg):
    with open("e2e_failures.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

from app.models.policy import Policy  # Import to ensure model registration if needed
# (Assuming other models registered via app.main or conftest imports)

# Integration Scenario:
# 1. Admin hires a new Agent.
# 2. Admin creates a Client.
# 3. New Agent sells a Policy to the Client.
# 4. Admin processes Payment for the Policy.
# 5. Commission is generated for Agent.
# 6. Admin runs Payroll for the month.
# 7. Validation:
#    - Policy is Active.
#    - Payment is Completed.
#    - Commission exists.
#    - Payroll Record exists.
#    - General Ledger is balanced.
#    - Analytics dashboard reflects Revenue & Expenses.

from app.models.employee import EmployeeProfile

def test_full_business_lifecycle(client, db_session, test_company, auth_headers):
    # ----------------------------------------------------------------
    # 1. HR Setup: Hire a new Sales Agent (using Admin Auth)
    # ----------------------------------------------------------------
    new_agent_data = {
        "email": "lifecycle_agent@test.com",
        "password": "agentpassword123",
        "first_name": "Lifecycle",
        "last_name": "Agent",
        "role": "agent",
        "is_active": True
    }
    
    # Using API to create employee if possible, but for simplicity/reliability in this test 
    # and to ensure Profile Creation (which API might handle behind scenes), we use DB directly 
    # or assume API does it. 
    # API POST /users/ usually just creates User. 
    # POST /employees/ usually creates User + Profile.
    # Let's stick to DB creation to be 100% sure we have the Profile setup correctly for Payroll.
    
    agent = User(
        company_id=test_company.id,
        email=new_agent_data["email"],
        password_hash=get_password_hash(new_agent_data["password"]),
        first_name=new_agent_data["first_name"],
        last_name=new_agent_data["last_name"],
        role=new_agent_data["role"],
        is_active=True
    )
    db_session.add(agent)
    db_session.flush() # Get ID
    
    profile = EmployeeProfile(
        user_id=agent.id,
        base_salary=500000.00,
        currency="XOF",
        payment_method="bank_transfer",
        job_title="Sales Agent",
        department="Sales"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(agent)
    agent_id = str(agent.id)

    print("STEP 1: AGENT CREATED")

    # Authenticate as the new Agent
    login_res = client.post("/api/v1/auth/login", json={"email": "lifecycle_agent@test.com", "password": "agentpassword123"})
    assert login_res.status_code == 200
    agent_token = login_res.json()["access_token"]
    agent_headers = {"Authorization": f"Bearer {agent_token}"}

    # ----------------------------------------------------------------
    # 2. Setup Client (Admin does this or Agent)
    # ----------------------------------------------------------------
    client_data = {
        "client_type": "individual",
        "first_name": "Test",
        "last_name": "Client",
        "email": "client@lifecycle.com",
        "phone": "+225 0102030405",
        "company_id": str(test_company.id)
    }
    # Assuming POST /clients/ exists
    res = client.post("/api/v1/clients/", json=client_data, headers=auth_headers)
    if res.status_code != 201:
        print(f"CLIENT CREATION ERROR: {res.text}") 
    assert res.status_code == 201, f"Client creation failed: {res.text}"
    client_id = res.json()["id"]
    print("STEP 2: CLIENT CREATED")
    
    # ----------------------------------------------------------------
    # 3. Sales: Agent sells a Policy
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    # 2.5 Setup Policy Type (Required for Policy)
    # ----------------------------------------------------------------
    from app.models.policy_type import PolicyType
    policy_type = PolicyType(
        company_id=test_company.id,
        name="Auto Insurance",
        code="AUTO",
        description="Standard Auto",
        is_active=True
    )
    db_session.add(policy_type)
    db_session.commit()
    db_session.refresh(policy_type)
    print("STEP 2.5: POLICY TYPE CREATED")

    # ----------------------------------------------------------------
    # 3. Sales: Agent sells a Policy
    # ----------------------------------------------------------------
    # Policy: 1,000,000 XOF Premium
    policy_data = {
        "client_id": client_id,
        "policy_type_id": str(policy_type.id),
        "premium_amount": 1000000.0,
        "start_date": str(date.today()),
        "end_date": str(date.today().replace(year=date.today().year + 1)),
        "premium_frequency": "annual",
        "sales_agent_id": agent_id
    }
    
    # Create Quote first? Or direct Policy? Assuming direct policy creation is allowed for Agent or Quote->Policy flow.
    # Let's try direct policy creation if endpoint supports it, otherwise create quote then convert.
    # Checking policy endpoints...    # Assuming POST /policies/ exists
    print(f"DEBUG: policy_data type={type(policy_data)} value={policy_data}")
    res = client.post("/api/v1/policies/", json=policy_data, headers=auth_headers)
    if res.status_code != 201:
        log_error(f"POLICY CREATION ERROR: {res.text}")
    assert res.status_code == 201, f"Policy creation failed: {res.text}"
    policy_id = res.json()["id"]
    
    # Verify Policy Active
    res = client.get(f"/api/v1/policies/{policy_id}", headers=auth_headers)
    if res.status_code != 200: log_error(f"GET POLICY ERROR: {res.text}")
    assert res.json()["status"] == "active"
    print("STEP 3: POLICY SOLD")
    
    # ----------------------------------------------------------------
    # 4. Finance: Process Payment
    # ----------------------------------------------------------------
    # One-time full payment
    payment_data = {
        "policy_id": policy_id,
        "amount": 1000000.0,
        "payment_details": {
            "method": "mobile_money",
            "gateway": "orange_money",
            "phone_number": "+2250102030405",
            "operator_transaction_id": "TXN-001"
        }
    }
    res = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
    if res.status_code != 201: log_error(f"PAYMENT ERROR: {res.text}")
    assert res.status_code == 201, f"Payment processing failed: {res.text}"
    print("STEP 4: PAYMENT PROCESSED")
    
    # Verify Payment recorded
    # Verify Commission generated (10% of 1M = 100,000)
    # Check commissions endpoint
    res = client.get("/api/v1/commissions/", headers=auth_headers) # Admin viewing all
    if res.status_code != 200: log_error(f"GET COMMISSIONS ERROR: {res.text}")
    assert res.status_code == 200
    commissions = res.json()
    # Find our specific commission
    agent_commissions = [c for c in commissions if c["agent_id"] == agent_id]
    assert len(agent_commissions) >= 1
    assert float(agent_commissions[0]["amount"]) == 100000.0
    print("STEP 4.5: COMMISSION VERIFIED")

    # ----------------------------------------------------------------
    # 5. HR: Run Payroll
    # ----------------------------------------------------------------
    # Run payroll for current month
    payroll_payload = {
        "month": date.today().strftime("%Y-%m")
    }
    res = client.post("/api/v1/payroll/generate", json=payroll_payload, headers=auth_headers)
    if res.status_code != 200: log_error(f"PAYROLL ERROR: {res.text}")
    assert res.status_code == 200, f"Payroll generation failed: {res.text}"
    print("STEP 5: PAYROLL RUN")
    
    # Verify Payroll Record for Agent
    # Should Include Base (500k) + Commission (100k) = 600k Gross
    res = client.get(f"/api/v1/payroll/?employee_id={agent_id}", headers=auth_headers)
    if res.status_code != 200: log_error(f"GET PAYROLL HISTORY ERROR: {res.text}")
    assert res.status_code == 200
    pay_history = res.json()
    assert len(pay_history) >= 1
    latest_pay = pay_history[0]
    assert float(latest_pay["base_salary"]) == 500000.0
    assert float(latest_pay["commissions_total"]) == 100000.0
    assert float(latest_pay["amount"]) == 600000.0 # Gross
    print("STEP 5.5: PAYROLL VERIFIED")

    # ----------------------------------------------------------------
    # 6. Accounting: Validate Ledger
    # ----------------------------------------------------------------
    # Check Trial Balance
    res = client.get("/api/v1/accounting/trial-balance", headers=auth_headers)
    if res.status_code != 200: log_error(f"GET TRIAL BALANCE ERROR: {res.text}")
    assert res.status_code == 200
    tb = res.json()
    print("STEP 6: LEDGER VERIFIED")
    
    # Verify Total Debits == Total Credits (Balance)
    total_debit = sum(float(acct["total_debit"]) for acct in tb)
    total_credit = sum(float(acct["total_credit"]) for acct in tb)
    assert total_debit == total_credit
    assert total_debit > 0 # Ensure transactions actually happened
    
    # Check specific accounts functionality
    # Premium Income (4000): Credit 1,000,000
    premium_income = next((a for a in tb if a["account_code"] == "4000"), None)
    assert premium_income is not None
    assert float(premium_income["total_credit"]) == 1000000.0
    
    # Salary Expense (5000): Debit 500,000 (Base)
    salary_expense = next((a for a in tb if a["account_code"] == "5000"), None)
    assert salary_expense is not None
    assert float(salary_expense["total_debit"]) == 500000.0
    
    # Commission Expense (5100): Debit 100,000 (10% of 1M)
    comm_expense = next((a for a in tb if a["account_code"] == "5100"), None)
    assert comm_expense is not None
    assert float(comm_expense["total_debit"]) == 100000.0
    print("STEP 6.5: ACCOUNTS VERIFIED")
    
    # ----------------------------------------------------------------
    # 7. Analytics Dashboard
    # ----------------------------------------------------------------
    analytics_filter = {
        "company_id": str(test_company.id),
        "start_date": str(date.today() - timedelta(days=1)), # Ensure range covers today
        "end_date": str(date.today() + timedelta(days=1)),
        "period_type": "custom",
        "scope": "company"
    }
    res = client.post("/api/v1/analytics/dashboard", json=analytics_filter, headers=auth_headers)
    if res.status_code != 200: log_error(f"GET ANALYTICS ERROR: {res.text}")
    assert res.status_code == 200
    dashboard = res.json()
    print("STEP 7: ANALYTICS VERIFIED")
    
    # Check Financials
    fin = dashboard["financials"]
    assert float(fin["total_revenue"]["value"]) == 1000000.0
    # Expenses should track Salary Expense (500k) + Commission (100k) = 600k
    assert float(fin["total_expenses"]["value"]) >= 600000.0
    
    # Check Operations
    ops = dashboard["operations"]
    assert int(ops["total_policies"]["value"]) >= 1
    
    # Check Performance (Top Agents)
    perf = dashboard["performance"]
    agent_rank = next((a for a in perf["top_agents"] if a["name"] == "Lifecycle Agent"), None)
    assert agent_rank is not None
    assert float(agent_rank["sales"]) == 1000000.0
    assert int(agent_rank["count"]) == 1
