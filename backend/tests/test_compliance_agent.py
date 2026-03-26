import asyncio
import httpx
import json

AGENT_URL = "http://localhost:8038/"

async def test_compliance_screening(first_name, last_name, email):
    print(f"\n--- Testing Screening for: {first_name} {last_name} ({email}) ---")
    data = {
        "message": {
            "text": json.dumps({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": "123456789",
                "role": "client"
            })
        },
        "context": {"google_api_key": "dummy_key"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(AGENT_URL, json=data, timeout=10.0)
            if response.status_code == 200:
                result = json.loads(response.json()["messages"][-1]["text"])
                print(f"Status: {result.get('status').upper()}")
                print(f"High Risk: {result.get('is_high_risk')}")
                print(f"Notes: {result.get('notes')}")
                print(f"Risk Score: {result.get('risk_score')}")
            else:
                print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Failed: {str(e)}")

async def main():
    print("Verifying Compliance & AML Agent Logic...")
    
    # Test 1: Clean User
    await test_compliance_screening("John", "Doe", "john.doe@example.com")
    
    # Test 2: Sanctioned Name
    await test_compliance_screening("Ivan", "the Terrible", "ivan@history.com")
    
    # Test 3: Sanctioned Email
    await test_compliance_screening("Normal", "Person", "sanctioned_email@example.com")

if __name__ == "__main__":
    asyncio.run(main())
