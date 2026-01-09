import asyncio
import os
import sys
import uuid
import json
from datetime import datetime

# Setup Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend/.env")))

from backend.agents.a2a_support_agent.agent_executor import SupportAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

class MockEvent:
    def __init__(self, type, text=None, path=None):
        self.type = type
        self.text = text
        self.path = path

from app.core.database import SessionLocal
from app.models.user import User
from app.models.policy import Policy
from app.models.claim import Claim

async def verify_multimodal():
    print("🚀 Starting Multi-modal Claims Verification...")
    
    db = SessionLocal()
    # Get any policy to use for testing
    policy = db.query(Policy).first()
    if not policy:
        print("❌ No policies found in database.")
        db.close()
        return

    print(f"✅ Found Test Policy: {policy.policy_number}")
    client_id = str(policy.client_id)
    company_id = str(policy.company_id)
    
    executor = SupportAgentExecutor()
    event_queue = EventQueue()
    
    # Simulate first turn: User uploads image and describes incident
    ctx1 = RequestContext(
        metadata={
            "client_id": client_id,
            "company_id": company_id,
            "google_api_key": os.getenv("GOOGLE_API_KEY")
        },
        events=[
            MockEvent(type="user_text_message", text=f"I just noticed a deep scratch on my car door. Here is a photo."),
            MockEvent(type="user_image_message", path=os.path.abspath("backend/data/samples/car_scratch.png"))
        ]
    )
    
    print("\n[TURN 1] Sending image to agent...")
    await executor.execute(ctx1, event_queue)
    
    if not event_queue.events:
        print("❌ Agent did not respond in Turn 1.")
        db.close()
        return
        
    event1 = event_queue.events[-1]
    response1 = event1.get("text", "") if isinstance(event1, dict) else getattr(event1, "text", "")
    print(f"\n[AGENT RESPONSE 1]:\n{response1}")
    
    # Check if agent used analyze_incident_image
    if "scratch" in response1.lower() or "severity" in response1.lower() or "assessment" in response1.lower():
        print("\n✅ Agent successfully analyzed the image and described the damage.")
    else:
        print("\n❌ Agent did not seem to analyze the damage accurately.")

    # Simulate second turn: User confirms they want to open a claim
    ctx2 = RequestContext(
        metadata=ctx1.metadata,
        events=[
            MockEvent(type="user_text_message", text=f"Yes, please go ahead and open a claim for policy {policy.policy_number}.")
        ]
    )
    
    print("\n[TURN 2] Confirming claim registration...")
    # Clear queue or use a fresh one
    event_queue2 = EventQueue()
    await executor.execute(ctx2, event_queue2)
    
    if not event_queue2.events:
        print("❌ Agent did not respond in Turn 2.")
        db.close()
        return
        
    event2 = event_queue2.events[-1]
    response2 = event2.get("text", "") if isinstance(event2, dict) else getattr(event2, "text", "")
    print(f"\n[AGENT RESPONSE 2]:\n{response2}")
    
    if "claim" in response2.lower() and ("successfully" in response2.lower() or "filed" in response2.lower()):
        print("\n✅ Agent successfully filed the automated claim.")
        
        # Verify in database
        db.expire_all()
        claim = db.query(Claim).filter(Claim.policy_id == policy.id).order_by(Claim.created_at.desc()).first()
        if claim:
            print(f"✅ Claim Record Found: {claim.claim_number}")
            print(f"   Severity Assessment: {claim.ai_assessment.get('severity_score')}")
            print(f"   Estimated Cost: ${claim.claim_amount}")
        else:
            print("❌ Claim record not found in database.")
    else:
        print("\n❌ Agent failed to complete the claim registration.")

    db.close()

if __name__ == "__main__":
    asyncio.run(verify_multimodal())
