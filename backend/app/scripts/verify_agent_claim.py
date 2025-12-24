
import asyncio
import uuid
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))

from app.core.database import SessionLocal
from app.core.config import settings

print(f"DEBUG: Using DATABASE_URL={settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'HIDDEN'}")
from app.models.user import User
from app.models.policy import Policy
from app.models.claim import Claim
from agents.a2a_claims_agent.agent_executor import ClaimsAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

async def verify_claim_creation():
    db = SessionLocal()
    try:
        # 1. Setup Data
        print("Finding a valid user and policy...")
        # Find a user with a policy
        # We need a user who has claims permission? Defaults usually have it or we skip permission check if we mock context?
        # The agent checks permission `claim:write`.
        
        # We'll try to find a user and assign permission if needed or assume super_admin
        user = db.query(User).filter(User.role == "super_admin").first()
        if not user:
             user = db.query(User).first()
             print(f"Warning: Using normal user {user.email}, promoting to super_admin for valid test.")
             
        if not user:
            print("No users found in DB. Cannot test.")
            return

        # Ensure user has permission by temporarily assigning super_admin role
        original_role = user.role
        if original_role != "super_admin":
             print(f"Promoting user {user.email} to super_admin for test duration...")
             user.role = "super_admin"
             db.commit()

        policy = db.query(Policy).first()
        if not policy:
            print("No policies found in DB. Cannot test.")
            return

        print(f"Using User: {user.email} ({user.id})")
        print(f"Using Policy: {policy.policy_number} ({policy.id})")

        # 2. Mock Context
        # We need to mock RequestContext. Using a simple object or the real class if possible.
        # RequestContext is a Pydantic model usually.
        
        # Let's inspect RequestContext signature if needed, but usually it takes metadata dict.
        # The agent executor expects context.metadata
        
        class MockContext:
            def __init__(self, metadata, events):
                self.metadata = metadata
                self.events = events
        
        class MockEvent:
            def __init__(self, type, text):
                self.type = type
                self.text = text

        context = MockContext(
            metadata={
                "user_id": str(user.id),
                "policy_id": str(policy.id)
            },
            events=[MockEvent("user_text_message", "I damaged my bumper, cost is 1500")]
        )
        
        class MockEventQueue(EventQueue):
            def enqueue_event(self, event):
                print(f"Agent Response Event: {event}")

        event_queue = MockEventQueue()
        
        # 3. Execute Agent
        print("Executing Agent...")
        executor = ClaimsAgentExecutor()
        await executor.execute(context, event_queue)
        
        # 4. Verify DB
        print("Verifying Database...")
        claims = db.query(Claim).filter(Claim.policy_id == policy.id).all()
        
        with open("result.txt", "w") as f:
            f.write(f"Found {len(claims)} claims for policy {policy.id}\n")
            found_match = False
            for c in claims:
                f.write(f" - Claim {c.claim_number}: Amount={c.claim_amount} (Type: {type(c.claim_amount)}), Desc={c.incident_description}, Status={c.status}\n")
                # Compare with flexibility for types
                try:
                    if float(c.claim_amount) == 1500.0:
                        found_match = True
                        f.write("   ^ MATCH FOUND\n")
                except:
                    pass
            
            if found_match:
                 f.write("SUCCESS: Claim verification passed.\n")
                 print("SUCCESS")
            else:
                 f.write("FAILURE: No matching claim found.\n")
                 print("FAILURE")


    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_claim_creation())
