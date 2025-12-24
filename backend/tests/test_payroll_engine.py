import requests
import uuid
import time
import sys
from datetime import datetime

def log(msg):
    print(msg)
    sys.stdout.flush()

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@demoinsurance.com"
ADMIN_PASSWORD = "Admin123!"

def test_automated_payroll_flow():
    # 1. Login
    log("Logging in...")
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        log(f"Login failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    log("LoggedIn.")

    # 2. Get current user info
    user_me = requests.get(f"{BASE_URL}/auth/me", headers=headers).json()
    my_id = user_me["id"]
    log(f"Running as: {user_me['first_name']} {user_me['last_name']} (ID: {my_id})")

    # Create Client
    log("STEP: Creating client...")
    client_data = {
        "client_type": "individual",
        "first_name": "Payroll",
        "last_name": "Tester",
        "email": f"payroll_test_{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+22500000000",
        "risk_profile": "medium",
        "kyc_status": "verified"
    }
    client_res_full = requests.post(f"{BASE_URL}/clients/", json=client_data, headers=headers)
    if not client_res_full.ok:
        log(f"FAILURE_CLIENT_CREATE: {client_res_full.status_code} - {client_res_full.text}")
        return
    client_id = client_res_full.json()["id"]
    log(f"SUCCESS: Client created {client_id}")

    # Get first policy type
    log("STEP: Fetching policy type...")
    pt_res_full = requests.get(f"{BASE_URL}/policy-types/", headers=headers)
    if not pt_res_full.ok:
        log(f"FAILURE_PTYPES_FETCH: {pt_res_full.text}")
        return
    pt_res = pt_res_full.json()
    ptypes = pt_res if isinstance(pt_res, list) else pt_res.get("policy_types", [])
    if not ptypes:
        log("No policy types found.")
        return
    ptype_id = ptypes[0]["id"]

    # Create Policy
    log("STEP: Creating policy...")
    today = datetime.now().strftime("%Y-%m-%d")
    next_year = (datetime.now().year + 1)
    expiry = f"{next_year}-{datetime.now().strftime('%m-%d')}"
    
    policy_data = {
        "client_id": client_id,
        "policy_type_id": ptype_id,
        "policy_number": f"POL-PAYROLL-{int(time.time())}",
        "start_date": today,
        "end_date": expiry,
        "premium_amount": 1000000,
        "status": "active",
        "sales_agent_id": my_id
    }
    pol_res_full = requests.post(f"{BASE_URL}/policies/", json=policy_data, headers=headers)
    if not pol_res_full.ok:
        log(f"FAILURE_POLICY_CREATE: {pol_res_full.status_code} - {pol_res_full.text}")
        return
    policy_id = pol_res_full.json()["id"]
    log(f"SUCCESS: Policy created {policy_id}")

    # Process Payment
    log("STEP: Processing payment...")
    payment_data = {
        "policy_id": policy_id,
        "amount": 1000000,
        "payment_details": {
            "method": "cash",
            "gateway": "manual"
        }
    }
    pay_res = requests.post(f"{BASE_URL}/payments/process", json=payment_data, headers=headers)
    if not pay_res.ok:
        log(f"FAILURE_PAYMENT_PROCESS: {pay_res.status_code} - {pay_res.text}")
        return
    log("SUCCESS: Payment processed.")

    # 4. Generate Payroll
    log("Generating Payroll for current month...")
    current_month = datetime.now().strftime("%Y-%m")
    gen_res = requests.post(f"{BASE_URL}/payroll/generate", json={"month": current_month}, headers=headers)
    
    if gen_res.status_code != 200:
        log(f"Payroll generation failed: {gen_res.text}")
        return
    
    results = gen_res.json()
    log(f"Payroll generated for {len(results)} employees.")

    # 5. Verify agent's payroll item
    agent_payroll = None
    for item in results:
        if str(item["employee_id"]) == str(my_id):
            agent_payroll = item
            break
    
    if not agent_payroll:
        log("FAILURE: Agent not found in payroll run.")
        return

    log("VERIFICATION_START")
    log(f"VERIF_BASE_SALARY: {agent_payroll['base_salary']}")
    log(f"VERIF_COMMISSIONS: {agent_payroll['commissions_total']}")
    log(f"VERIF_GROSS: {agent_payroll['amount']}")
    log(f"VERIF_NET: {agent_payroll['net_pay']}")
    log(f"VERIF_TAX_IS: {agent_payroll['tax_is']}")
    log(f"VERIF_TAX_CN: {agent_payroll['tax_cn']}")
    log(f"VERIF_TAX_IGR: {agent_payroll['tax_igr']}")
    log(f"VERIF_TAX_CNPS: {agent_payroll['social_security_cnps']}")
    
    if float(agent_payroll['commissions_total']) >= 100000:
        log("VERIF_RESULT: SUCCESS_COMMISSIONS")
    else:
        log(f"VERIF_RESULT: WARNING_COMMISSIONS_{agent_payroll['commissions_total']}")
        
    if float(agent_payroll['tax_is']) > 0:
        log("VERIF_RESULT: SUCCESS_TAXES")
    
    log("VERIFICATION_END")

if __name__ == "__main__":
    test_automated_payroll_flow()
