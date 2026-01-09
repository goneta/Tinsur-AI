import asyncio
import os
import sys
import uuid
import json
from datetime import datetime, timedelta

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
from app.models.premium_schedule import PremiumSchedule

async def verify_proactive():
    print("🚀 Starting Proactive Support Verification...")
    
    db = SessionLocal()
    # 1. Setup Test Data: Ensure a policy exists with a late payment
    policy = db.query(Policy).first()
    if not policy:
        print("❌ No policies found. Please run seed script first.")
        return
        
    client_id = policy.client_id
    
    # Create an overdue schedule
    schedule = PremiumSchedule(
        id=uuid.uuid4(),
        company_id=policy.company_id,
        policy_id=policy.id,
        installment_number="Inst-PRO-V1",
        due_date=(datetime.now() - timedelta(days=10)).date(),
        amount=150.00,
        status='pending',
        late_fee=25.0,
        late_fee_applied=True
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    print(f"✅ Created Overdue Payment: Policy {policy.policy_number}, Due: {schedule.due_date}")
    
    executor = SupportAgentExecutor()
    event_queue = EventQueue()
    
    # Turn 1: User says "Hello" - Agent should see the alert and offer help
    ctx1 = RequestContext(
        metadata={
            "client_id": str(client_id),
            "company_id": str(policy.company_id),
            "google_api_key": os.getenv("GOOGLE_API_KEY")
        },
        events=[
            MockEvent(type="user_text_message", text="Hi, I have a quick question about my account.")
        ]
    )
    
    print("\n[TURN 1] Sending generic greeting to agent...")
    await executor.execute(ctx1, event_queue)
    
    event1 = event_queue.events[-1]
    response1 = event1.get("text", "") if isinstance(event1, dict) else getattr(event1, "text", "")
    print(f"\n[AGENT RESPONSE 1]:\n{response1}")
    
    if "late" in response1.lower() or "waive" in response1.lower() or "payment" in response1.lower():
        print("\n✅ Agent successfully identified the late payment proactively!")
    else:
        print("\n❌ Agent failed to proactively address the account state.")

    # Turn 2: User confirms they want to waive the fee
    ctx2 = RequestContext(
        metadata=ctx1.metadata,
        events=[
            MockEvent(type="user_text_message", text="Oh, I didn't realize it was late. Yes, if you could waive the fee that would be great!")
        ]
    )
    
    print("\n[TURN 2] Confirming fee waiver...")
    event_queue2 = EventQueue()
    await executor.execute(ctx2, event_queue2)
    
    event2 = event_queue2.events[-1]
    response2 = event2.get("text", "") if isinstance(event2, dict) else getattr(event2, "text", "")
    print(f"\n[AGENT RESPONSE 2]:\n{response2}")
    
    if "waived" in response2.lower() or "taken care of" in response2.lower():
        print("\n✅ Agent successfully waived the late fee.")
        
        # Verify in database
        db.expire_all()
        updated_schedule = db.query(PremiumSchedule).filter(PremiumSchedule.id == schedule.id).first()
        if updated_schedule and updated_schedule.status == 'waived':
            print("✅ Database verification successful: Status set to 'waived'.")
        else:
            print(f"❌ Database verification failed. Status: {updated_schedule.status}")
    else:
        print("\n❌ Agent failed to process the waiver.")

    # Cleanup (optional): Remove the test schedule
    # db.delete(schedule)
    # db.commit()
    db.close()

if __name__ == "__main__":
    asyncio.run(verify_proactive())
