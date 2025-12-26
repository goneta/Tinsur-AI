import asyncio
import httpx
import json

AGENT_URL = "http://localhost:8038/"

async def test_screening(description, payload):
    print(f"\n--- Testing: {description} ---")
    data = {
        "message": {
            "text": json.dumps(payload)
        },
        "context": {"google_api_key": "dummy_key"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(AGENT_URL, json=data, timeout=10.0)
            if response.status_code == 200:
                result = json.loads(response.json()["messages"][-1]["text"])
                print(f"Context: {result.get('context')}")
                print(f"Status: {result.get('status').upper()}")
                print(f"High Risk: {result.get('is_high_risk')}")
                print(f"Notes: {result.get('notes')}")
            else:
                print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Failed: {str(e)}")

async def main():
    print("Verifying Extended Compliance & AML Agent Logic...")
    
    # Test 1: Onboarding a Clean Client
    await test_screening("Onboarding Clean Client", {
        "context": "ONBOARDING",
        "first_name": "Alice",
        "last_name": "Wonderland",
        "email": "alice@rabbit.hole"
    })
    
    # Test 2: Payout to a Sanctioned Beneficiary
    await test_screening("Payout to Sanctioned Beneficiary", {
        "context": "PAYOUT",
        "claim_number": "CLM-20251226-TX99",
        "name": "Ivan the Terrible",
        "approved_amount": "50000.00"
    })
    
    # Test 3: Payout to a Fraudulent Email
    await test_screening("Payout to Sanctioned Email", {
        "context": "PAYOUT",
        "email": "payout_fraudster@danger.com",
        "approved_amount": "1200.00"
    })

if __name__ == "__main__":
    asyncio.run(main())
