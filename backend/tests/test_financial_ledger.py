import requests
import uuid
import time
import sys
from datetime import datetime
from decimal import Decimal

def log(msg):
    print(msg)
    sys.stdout.flush()

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@demoinsurance.com"
ADMIN_PASSWORD = "Admin123!"

def test_ledger_flow():
    # 1. Login
    log("Logging in...")
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=30)
    except requests.exceptions.Timeout:
        log("Login timed out after 30 seconds.")
        return
    
    if response.status_code != 200:
        log(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    log("LoggedIn.")

    # 2. Initialize Chart of Accounts if needed
    log("STEP: Initializing Chart of Accounts...")
    init_res = requests.post(f"{BASE_URL}/accounting/initialize", headers=headers, timeout=30)
    log(f"Init Result: {init_res.status_code}")

    # 3. Create a test payment to trigger ledger entry
    log("STEP: Creating test data for payment...")
    # Get a client/policy (reuse logic or fetch existing)
    clients_res = requests.get(f"{BASE_URL}/clients/", headers=headers, timeout=30).json()
    client_id = clients_res[0]["id"] if clients_res else None
    
    if not client_id:
        log("No client found for test.")
        return

    policies_res = requests.get(f"{BASE_URL}/policies/", headers=headers, timeout=30).json()
    # Handle both list and dict response formats
    policies_list = policies_res["policies"] if isinstance(policies_res, dict) and "policies" in policies_res else policies_res
    policy = policies_list[0] if isinstance(policies_list, list) and len(policies_list) > 0 else None
    
    if not policy:
        log("No policy found for test.")
        return
    
    # Process Payment (1,000,000 XOF)
    log(f"STEP: Processing payment of 1,000,000 XOF for policy {policy['policy_number']}...")
    payment_data = {
        "policy_id": policy["id"],
        "amount": 1000000,
        "payment_details": {
            "method": "cash",
            "gateway": "manual"
        }
    }
    pay_res = requests.post(f"{BASE_URL}/payments/process", json=payment_data, headers=headers, timeout=30)
    if not pay_res.ok:
        log(f"Payment failed: {pay_res.text}")
        return
    log("SUCCESS: Payment processed.")

    # 4. Verify Ledger Entry
    log("STEP: Verifying Ledger Entry...")
    ledger = requests.get(f"{BASE_URL}/accounting/ledger", headers=headers, timeout=30).json()
    
    found_payment_entry = False
    for entry in ledger:
        if f"Premium payment received for Policy {policy['policy_number']}" in entry["description"]:
            found_payment_entry = True
            log(f"SUCCESS: Found ledger entry: {entry['description']}")
            # Check balance
            total_debit = sum(float(e["debit"]) for e in entry["entries"])
            total_credit = sum(float(e["credit"]) for e in entry["entries"])
            if total_debit == total_credit == 1000000.0:
                log("VERIF_RESULT: SUCCESS_LEDGER_BALANCED")
            else:
                log(f"VERIF_RESULT: ERROR_LEDGER_UNBALANCED: D={total_debit} C={total_credit}")
            break
    
    if not found_payment_entry:
        log("FAILURE: Payment ledger entry not found.")

    # 6. Generate Payroll
    log("STEP: Generating Payroll for current month...")
    current_month = datetime.now().strftime("%Y-%m")
    gen_res = requests.post(f"{BASE_URL}/payroll/generate", json={"month": current_month}, headers=headers, timeout=30)
    
    if gen_res.status_code != 200:
        log(f"Payroll generation failed: {gen_res.text}")
    else:
        log("SUCCESS: Payroll processed. Verifying ledger...")
        ledger = requests.get(f"{BASE_URL}/accounting/ledger", headers=headers, timeout=30).json()
        found_payroll_entry = False
        for entry in ledger:
            if f"Payroll Consolidation for {current_month}" in entry["description"]:
                found_payroll_entry = True
                log(f"SUCCESS: Found payroll ledger entry: {entry['description']}")
                total_debit = sum(float(e["debit"]) for e in entry["entries"])
                total_credit = sum(float(e["credit"]) for e in entry["entries"])
                if abs(total_debit - total_credit) < 0.01:
                    log(f"VERIF_RESULT: SUCCESS_PAYROLL_BALANCED (Total: {total_debit})")
                else:
                    log(f"VERIF_RESULT: ERROR_PAYROLL_UNBALANCED: D={total_debit} C={total_credit}")
                break
        if not found_payroll_entry:
            log("FAILURE: Payroll ledger entry not found.")

    # 7. Final Trial Balance Check
    log("STEP: Final Trial Balance Check...")
    tb = requests.get(f"{BASE_URL}/accounting/trial-balance", headers=headers, timeout=30).json()
    for item in tb:
        log(f"ACCOUNT {item['account_code']} ({item['account_name']}): {item['balance']}")

    log("VERIFICATION_END")

if __name__ == "__main__":
    test_ledger_flow()
