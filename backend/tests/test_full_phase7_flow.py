import requests
import json
from datetime import datetime, date, timedelta
import uuid
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
EMAIL = "admin@demoinsurance.com"
PASSWORD = "Admin123!"

def print_step(message):
    print(f"\n{'='*50}")
    print(f"STEP: {message}")
    print(f"{'='*50}")

def print_result(message, success=True):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

class Phase7Tester:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {}
        self.company_id = None
        self.partner_company_id = None
        self.client_id = None
        self.policy_type_id = None
        self.quote_id = None
        self.policy_id = None
        self.payment_id = None
        self.claim_id = None

    def login(self):
        print_step("Logging in")
        resp = self.session.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        resp.raise_for_status()
        token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}
        self.session.headers.update(self.headers)
        
        me_resp = self.session.get(f"{BASE_URL}/auth/me")
        self.company_id = me_resp.json()["company_id"]
        print_result(f"Logged in. Company ID: {self.company_id}")

    def setup_partner_company(self):
        print_step("Ensuring Partner Company exists")
        # In a real test we might create it, but let's assume 'Partner Insurer' exists or we can use another one
        # From previous list: ['Demo Insurance Company', 'Test Company', 'Lead Insurer', 'Partner Insurer', 'Demo Insurance Co']
        # Let's try to find 'Partner Insurer'
        # There is no direct list companies endpoint for non-superadmins usually, but let's try a workaround
        # or just use a hardcoded search if we have to.
        # Actually, as admin we might not see other companies. 
        # For co-insurance, we need IDs of other companies.
        # Let's use a quick Python script to get a valid partner company ID from the DB.
        pass

    def get_resources(self):
        print_step("Getting Client and Policy Type")
        # Client
        clients = self.session.get(f"{BASE_URL}/clients/").json()
        if clients:
            self.client_id = clients[0]['id']
            print_result(f"Using existing client: {self.client_id}")
        else:
            client_data = {
                "company_id": self.company_id,
                "client_type": "individual",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "phone": "+2250102030405",
                "first_name": "Phase7",
                "last_name": "Tester",
                "date_of_birth": "1990-01-01",
                "city": "Abidjan",
                "country": "Côte d'Ivoire"
            }
            client = self.session.post(f"{BASE_URL}/clients/", json=client_data).json()
            self.client_id = client['id']
            print_result(f"Created client: {self.client_id}")

        # Policy Type
        pt_resp = self.session.get(f"{BASE_URL}/policy-types/").json()
        types = pt_resp.get("policy_types", [])
        if types:
            self.policy_type_id = types[0]['id']
            print_result(f"Using policy type: {types[0]['name']}")
        else:
            print_result("No policy types found", False)
            exit(1)

    def create_policy_flow(self):
        print_step("Create Quote and Convert to Policy")
        quote_data = {
            "client_id": self.client_id,
            "policy_type_id": self.policy_type_id,
            "coverage_amount": 10000000,
            "premium_amount": 500000,
            "final_premium": 450000,
            "duration_months": 12,
            "premium_frequency": "annual"
        }
        quote = self.session.post(f"{BASE_URL}/quotes/", json=quote_data).json()
        self.quote_id = quote['id']
        print_result(f"Quote created: {self.quote_id}")

        convert_data = {
            "start_date": date.today().isoformat(),
            "payment_method": "cash",
            "initial_payment_amount": 450000
        }
        policy = self.session.post(f"{BASE_URL}/quotes/{self.quote_id}/convert", json=convert_data).json()
        self.policy_id = policy['policy_id']
        print_result(f"Policy created: {self.policy_id}")

    def verify_co_insurance(self, partner_id):
        print_step("Setting up Co-Insurance and Processing Payment")
        # 1. Setup co-insurance share (30% to partner)
        # We need to do this via DB or if there is an endpoint. 
        # Looking at policy_service.py, there is no direct endpoint for creating shares shown in previous research.
        # Let's assume we can use a helper script to inject it or if there is an undocumented endpoint.
        # Wait, I can use run_command to run a python snippet that adds the share to the DB.
        pass

    def run_full_test(self, partner_id):
        try:
            self.login()
            self.get_resources()
            self.create_policy_flow()
            
            # Inject Co-insurance share for this policy
            print(f"Injecting 30% co-insurance share for partner: {partner_id}")
            inject_cmd = f"python -c \"from app.core.database import SessionLocal; from app.models.co_insurance import CoInsuranceShare; db=SessionLocal(); share=CoInsuranceShare(policy_id='{self.policy_id}', company_id='{partner_id}', share_percentage=30, fee_percentage=5); db.add(share); db.commit(); db.close()\""
            import subprocess
            subprocess.run(inject_cmd, shell=True, check=True)
            print_result("Co-insurance share injected")

            # Process Payment
            print_step("Processing Payment & Verifying Distribution")
            payment_data = {
                "policy_id": self.policy_id,
                "amount": 450000,
                "payment_details": {
                    "method": "cash",
                    "reference_number": f"VERIFY-{uuid.uuid4().hex[:6].upper()}"
                }
            }
            payment_resp = self.session.post(f"{BASE_URL}/payments/process", json=payment_data)
            payment_resp.raise_for_status()
            self.payment_id = payment_resp.json()['id']
            print_result(f"Payment processed: {self.payment_id}")

            # Verify Inter-company share (Premium Distribution)
            # 30% of 450,000 = 135,000. 
            # 5% fee on 135,000 = 6,750. 
            # Net distribution = 135,000 - 6,750 = 128,250.
            print("Verifying inter-company share in DB...")
            verify_cmd = f"python -c \"from app.core.database import SessionLocal; from app.models.inter_company_share import InterCompanyShare; db=SessionLocal(); share=db.query(InterCompanyShare).filter(InterCompanyShare.resource_id=='{self.payment_id}', InterCompanyShare.resource_type=='premium_distribution').first(); print(share.amount if share else 'NOT_FOUND'); db.close()\""
            result = subprocess.check_output(verify_cmd, shell=True).decode().strip()
            if result == '128250.00':
                print_result(f"Premium distribution verified: {result}")
            else:
                print_result(f"Premium distribution verification FAILED. Got: {result}, Expected: 128250.00", False)

            # Create and Approve Claim
            print_step("Creating and Approving Claim")
            claim_data = {
                "company_id": str(self.company_id),
                "policy_id": str(self.policy_id),
                "incident_date": date.today().isoformat(),
                "incident_description": "Test claim for co-insurance verification",
                "incident_location": "Abidjan",
                "claim_amount": 1000000,
                "created_by": str(uuid.uuid4()) # Temporary
            }
            # Need to get user ID for created_by
            user_data = self.session.get(f"{BASE_URL}/auth/me").json()
            claim_data["created_by"] = user_data["id"]

            claim_resp = self.session.post(f"{BASE_URL}/claims/", json=claim_data)
            claim_resp.raise_for_status()
            self.claim_id = claim_resp.json()['id']
            print_result(f"Claim created: {self.claim_id}")

            # Approve Claim
            approve_data = {
                "status": "approved",
                "approved_amount": 1000000
            }
            self.session.put(f"{BASE_URL}/claims/{self.claim_id}", json=approve_data).raise_for_status()
            print_result("Claim approved")

            # Verify Inter-company share (Claim Settlement)
            # 30% of 1,000,000 = 300,000.
            print("Verifying claim settlement in DB...")
            verify_claim_cmd = f"python -c \"from app.core.database import SessionLocal; from app.models.inter_company_share import InterCompanyShare; db=SessionLocal(); share=db.query(InterCompanyShare).filter(InterCompanyShare.resource_id=='{self.claim_id}', InterCompanyShare.resource_type=='claim_settlement').first(); print(share.amount if share else 'NOT_FOUND'); db.close()\""
            claim_result = subprocess.check_output(verify_claim_cmd, shell=True).decode().strip()
            if claim_result == '300000.00':
                print_result(f"Claim settlement verified: {claim_result}")
            else:
                print_result(f"Claim settlement verification FAILED. Got: {claim_result}, Expected: 300000.00", False)

            print("\n" + "*"*50)
            print("PHASE 7 VERIFICATION COMPLETE")
            print("*"*50)

        except Exception as e:
            print_result(f"Test failed with error: {str(e)}", False)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Get a partner company ID first
    import subprocess
    get_partner_cmd = "python -c \"from app.core.database import SessionLocal; from app.models.company import Company; db=SessionLocal(); c=db.query(Company).filter(Company.name=='Partner Insurer').first(); print(c.id if c else 'NONE'); db.close()\""
    partner_id = subprocess.check_output(get_partner_cmd, shell=True).decode().strip()
    
    if partner_id == 'NONE':
        # Create partner if not exists
        create_partner_cmd = "python -c \"from app.core.database import SessionLocal; from app.models.company import Company; db=SessionLocal(); c=Company(name='Partner Insurer', domain='partner.com'); db.add(c); db.commit(); print(c.id); db.close()\""
        partner_id = subprocess.check_output(create_partner_cmd, shell=True).decode().strip()
        print(f"Created Partner Insurer: {partner_id}")
    else:
        print(f"Using existing Partner Insurer: {partner_id}")

    tester = Phase7Tester()
    tester.run_full_test(partner_id)
