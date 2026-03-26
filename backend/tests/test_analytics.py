
import requests
import json
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@demoinsurance.com"
ADMIN_PASSWORD = "Admin123!"

def login():
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        if response.status_code != 200:
             logger.error(f"Login failed: {response.text}")
             sys.exit(1)
        return response.json()["access_token"]
    except Exception as e:
        logger.error(f"Login failed: {e}")
        sys.exit(1)

def test_analytics(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test Dashboard
    logger.info("Testing Dashboard endpoint...")
    filter_data = {
        "period_type": "month",
        "scope": "company",
        "company_id": "85ecdbd1-d151-4cd8-850b-53efc4ac1cb8" # Using ID from log or just fetching user first
    }
    
    # Needs valid company ID. Let's fetch current user company/me first.
    user_resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if user_resp.status_code != 200:
        logger.error(f"Failed to fetch user: {user_resp.status_code} {user_resp.text}")
        return

    user_data = user_resp.json()
    logger.info(f"User data: {user_data}")
    
    if "company_id" not in user_data:
        logger.error("company_id missing from user data")
        return
        
    company_id = user_data["company_id"]
    filter_data["company_id"] = company_id
    
    dash_resp = requests.post(f"{BASE_URL}/analytics/dashboard", json=filter_data, headers=headers)
    if dash_resp.status_code == 200:
        logger.info("Dashboard response received.")
        # logger.info(json.dumps(dash_resp.json(), indent=2))
        data = dash_resp.json()
        logger.info(f"Total Revenue: {data['financials']['total_revenue']['value']}")
    else:
        logger.error(f"Dashboard failed: {dash_resp.text}")
        
    # 2. Test Export
    logger.info("Testing Export endpoint...")
    export_resp = requests.post(
        f"{BASE_URL}/analytics/export?format=csv&report_type=financial_close",
        json=filter_data,
        headers=headers
    )
    if export_resp.status_code == 200:
        logger.info("Export response received.")
        content = export_resp.text
        logger.info(f"CSV Content Length: {len(content)}")
        logger.info(f"CSV Preview: {content[:100]}...")
    else:
         logger.error(f"Export failed: {export_resp.text}")

if __name__ == "__main__":
    logger.info("Starting Analytics Test...")
    token = login()
    test_analytics(token)
    logger.info("Analytics Test Completed.")
