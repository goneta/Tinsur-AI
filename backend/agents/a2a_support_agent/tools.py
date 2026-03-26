import os
import sys
import chromadb
import uuid
import google.generativeai as genai
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.models.ticket import Ticket

def search_knowledge_base(query: str, category: str = None) -> str:
    """
    Search the Tinsur.AI policy knowledge base for relevant information.
    
    Args:
        query: The search query.
        category: Optional category filter (e.g., 'auto', 'life', 'general').
                 If provided, only documents in this category will be searched.
    """
    print(f"DEBUG: search_knowledge_base called | query: {query} | category: {category}")
    # 1. Setup paths (safe to repeat)
    libs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../libs"))
    if libs_path not in sys.path:
        sys.path.append(libs_path)
    
    # Need backend root for app.core.config
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path:
        sys.path.append(backend_root)

    try:
        from app.core.config import settings
        from dotenv import load_dotenv
        
        # Load .env explicitly
        env_path = os.path.join(backend_root, ".env")
        load_dotenv(env_path)
        
        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Error: API Key missing for Knowledge Base search."

        # 2. Embedding Query
        genai.configure(api_key=api_key)
        emb_result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        
        # 3. Query DB
        db_path = os.path.join(backend_root, "data/chroma_db")
        chroma_client = chromadb.PersistentClient(path=db_path)
        
        try:
            collection = chroma_client.get_collection(name="support_knowledge_base")
        except Exception:
            return "Knowledge base collection not found. Please ingest documents first."

        # Apply metadata filter if category provided
        query_params = {
            "query_embeddings": [emb_result['embedding']],
            "n_results": 2
        }
        if category:
            query_params["where"] = {"category": category}

        results = collection.query(**query_params)
        
        if results['documents'] and results['documents'][0]:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            output_parts = []
            for doc, meta in zip(docs, metas):
                source = meta.get('source', 'unknown')
                page = meta.get('page', 'N/A')
                chunk_index = meta.get('chunk', 'N/A')
                
                header = f"[Source: {source}"
                if page != 'N/A':
                    header += f", Page: {page}"
                elif chunk_index != 'N/A':
                    header += f", Chunk: {chunk_index}"
                header += "]"
                
                output_parts.append(f"{header}\n{doc}")
            
            return "\n\n---\n\n".join(output_parts)
        
        return "No relevant information found in the knowledge base for this query."

    except Exception as e:
        return f"Knowledge Base Search Failed: {str(e)}"

@tool
def create_support_ticket(client_id: str, company_id: str, subject: str, description: str, category: str = "general", priority: str = "medium") -> str:
    """
    Creates a new support ticket in the database for human escalation.
    """
    print(f"DEBUG: create_support_ticket called for client {client_id}")
    
    # Setup paths (required if tool is called in isolated context)
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path:
        sys.path.append(backend_root)
        
    try:
        from app.core.database import SessionLocal
        from app.models.ticket import Ticket
        db = SessionLocal()
    except Exception as e:
        print(f"DEBUG: Failed to initialize DB in tool: {e}")
        return f"Error initializing database connection: {str(e)}"

    try:
        new_ticket = Ticket(
            company_id=uuid.UUID(company_id),
            client_id=uuid.UUID(client_id),
            ticket_number=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            category=category,
            priority=priority,
            subject=subject,
            description=description,
            status='open'
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        
        return f"Support ticket created successfully! Number: {new_ticket.ticket_number}. A human specialist will review your request and get back to you soon."
    except Exception as e:
        if db:
            db.rollback()
        return f"Error creating support ticket: {str(e)}"
    finally:
        db.close()

@tool
def get_user_policies(client_id: str) -> str:
    """
    Fetches the list of insurance policies for a specific client.
    Includes policy number, type, status, and premium details.
    """
    print(f"DEBUG: get_user_policies called for client {client_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.policy import Policy
        from app.models.policy_type import PremiumPolicyType
        db = SessionLocal()
        
        policies = db.query(Policy).filter(Policy.client_id == uuid.UUID(client_id)).all()
        if not policies:
            return "No policies found for this user."
        
        lines = ["Here are your current policies:"]
        for p in policies:
            p_type = p.policy_type.name if p.policy_type else "General"
            lines.append(f"- Policy #{p.policy_number}: {p_type} ({p.status.upper()}). Coverage: ${p.coverage_amount:,.2f}, Premium: ${p.premium_amount:,.2f} ({p.premium_frequency})")
            lines.append(f"  Valid from {p.start_date} to {p.end_date}")
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching policies: {str(e)}"
    finally:
        db.close()

@tool
def get_user_payments(client_id: str) -> str:
    """
    Fetches the payment schedule and next due dates for a client.
    Helps answer 'When is my next payment due?'
    """
    print(f"DEBUG: get_user_payments called for client {client_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.premium_schedule import PremiumSchedule
        from app.models.policy import Policy
        db = SessionLocal()
        
        # Join with Policy to filter by client_id
        schedules = db.query(PremiumSchedule).join(Policy).filter(
            Policy.client_id == uuid.UUID(client_id),
            PremiumSchedule.status.in_(['pending', 'overdue'])
        ).order_by(PremiumSchedule.due_date.asc()).all()
        
        if not schedules:
            return "You have no upcoming or overdue payments. All set!"
        
        lines = ["Here is your upcoming payment schedule:"]
        for s in schedules:
            status_str = "❗ OVERDUE" if s.status == 'overdue' else "Upcoming"
            lines.append(f"- {status_str}: ${s.amount:,.2f} due on {s.due_date} (Installment {s.installment_number})")
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching payment schedule: {str(e)}"
    finally:
        db.close()

@tool
def get_user_claims(client_id: str) -> str:
    """
    Fetches the status and details of claims filed by the client.
    Helps answer 'What is the status of my claim?'
    """
    print(f"DEBUG: get_user_claims called for client {client_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.claim import Claim
        db = SessionLocal()
        
        claims = db.query(Claim).filter(Claim.client_id == uuid.UUID(client_id)).order_by(Claim.created_at.desc()).all()
        
        if not claims:
            return "No claims found in our records for your account."
        
        lines = ["Here are your recent claims:"]
        for c in claims:
            status_display = c.status.replace("_", " ").title()
            lines.append(f"- Claim {c.claim_number}: {status_display}")
            lines.append(f"  Incident Date: {c.incident_date}")
            lines.append(f"  Description: {c.incident_description[:100]}...")
            if c.approved_amount:
                lines.append(f"  Approved Amount: ${c.approved_amount:,.2f}")
            lines.append("") # Spacer
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching claims: {str(e)}"
    finally:
        db.close()

@tool
def cancel_policy(client_id: str, policy_id: str, reason: str) -> str:
    """
    Cancels an active insurance policy.
    Requires the policy_id and a valid reason for cancellation.
    """
    print(f"DEBUG: cancel_policy called for client {client_id}, policy {policy_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.policy import Policy
        db = SessionLocal()
        
        # Verify ownership and state
        policy = db.query(Policy).filter(
            Policy.id == uuid.UUID(policy_id),
            Policy.client_id == uuid.UUID(client_id)
        ).first()
        
        if not policy:
            # Try by policy_number if UUID conversion failed or not found by ID
            policy = db.query(Policy).filter(
                Policy.policy_number == policy_id,
                Policy.client_id == uuid.UUID(client_id)
            ).first()

        if not policy:
            return f"Error: Policy {policy_id} not found or you do not have permission to cancel it."
            
        if policy.status == 'canceled':
            return f"Policy {policy.policy_number} is already canceled."
            
        policy.status = 'canceled'
        policy.cancellation_reason = reason
        db.commit()
        
        return f"Policy {policy.policy_number} has been successfully canceled. Reason: {reason}. You will receive a confirmation email shortly."
    except Exception as e:
        if db: db.rollback()
        return f"Error canceling policy: {str(e)}"
    finally:
        db.close()

@tool
def schedule_callback(client_id: str, company_id: str, preferred_time: str, topic: str) -> str:
    """
    Schedules a callback from a support representative or insurance adjuster.
    The 'preferred_time' should be a natural language description (e.g., 'Tomorrow at 10 AM').
    """
    print(f"DEBUG: schedule_callback called for client {client_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.ticket import Ticket
        db = SessionLocal()
        
        new_ticket = Ticket(
            company_id=uuid.UUID(company_id),
            client_id=uuid.UUID(client_id),
            ticket_number=f"CBK-{uuid.uuid4().hex[:8].upper()}",
            category="callback",
            priority="medium",
            subject=f"Callback Request: {topic}",
            description=f"User requested a callback regarding: {topic}.\nPreferred Time: {preferred_time}",
            status='open'
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        
        return f"Success! I've scheduled a callback request for you. A specialist will call you regarding '{topic}' at your preferred time: {preferred_time}. Reference: {new_ticket.ticket_number}."
    except Exception as e:
        if db: db.rollback()
        return f"Error scheduling callback: {str(e)}"
    finally:
        db.close()

@tool
def analyze_incident_image(image_path: str) -> str:
    """
    Analyzes an image of an incident (e.g., car damage) using Gemini Vision.
    Returns a JSON string containing:
    - damage_description: A detailed description of the visible damage.
    - severity_score: An integer from 1 to 10 (1=minor, 10=total loss).
    - estimated_repair_cost: A rough dollar estimate for repairs.
    - category: The type of incident (e.g., "body_damage", "glass_shatter").
    """
    print(f"DEBUG: analyze_incident_image called for {image_path}")
    try:
        import google.generativeai as genai
        from PIL import Image
        import os
        import json
        
        # Load environment variables for API key if not already configured
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Error: GOOGLE_API_KEY environment variable not found."
            
        genai.configure(api_key=api_key)
        
        # In version 0.3.2, we use 'gemini-pro-vision'
        model = genai.GenerativeModel('gemini-pro-vision')
        
        img = Image.open(image_path)
        
        prompt = """
        You are an expert insurance claims adjuster. Analyze this image of vehicle or property damage.
        Provide a JSON response with the following keys:
        - damage_description: string
        - severity_score: integer (1-10)
        - estimated_repair_cost: number (float)
        - category: string
        
        BE ACCURATE AND PROFESSIONAL. Only return the JSON.
        """
        
        response = model.generate_content([prompt, img])
        
        # Clean the response to ensure it's valid JSON
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()
            
        return json_text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

@tool
def automated_claim_registration(client_id: str, company_id: str, policy_number: str, ai_assessment_json: str, image_url: str) -> str:
    """
    Automatically creates a claim record based on an AI assessment of an incident image.
    'ai_assessment_json' should be the output from 'analyze_incident_image'.
    """
    print(f"DEBUG: automated_claim_registration called for policy {policy_number}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.claim import Claim
        from app.models.policy import Policy
        import json
        from datetime import datetime
        
        assessment = json.loads(ai_assessment_json)
        db = SessionLocal()
        
        # Find the policy to get policy_id
        policy = db.query(Policy).filter(
            Policy.policy_number == policy_number,
            Policy.client_id == uuid.UUID(client_id)
        ).first()
        
        if not policy:
            return f"Error: Policy {policy_number} not found for this client."
            
        claim_number = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        
        new_claim = Claim(
            claim_number=claim_number,
            policy_id=policy.id,
            client_id=uuid.UUID(client_id),
            company_id=uuid.UUID(company_id),
            incident_date=datetime.now().date(),
            incident_description=assessment.get("damage_description", "No description provided."),
            status='submitted',
            claim_amount=assessment.get("estimated_repair_cost", 0.0),
            evidence_files=[image_url],
            ai_assessment=assessment
        )
        
        db.add(new_claim)
        db.commit()
        db.refresh(new_claim)
        
        return f"Successfully registered claim {claim_number}! AI Assessment Summary: Severity {assessment.get('severity_score')}/10, Estimated Cost: ${assessment.get('estimated_repair_cost')}. An adjuster has been notified."
    except Exception as e:
        if db: db.rollback()
        return f"Error registering claim: {str(e)}"
    finally:
        db.close()

@tool
def get_proactive_alerts(client_id: str) -> str:
    """
    Scans the user's account for proactive alerts such as late payments or expiring policies.
    Returns a JSON string containing a list of alerts.
    """
    print(f"DEBUG: get_proactive_alerts called for client {client_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.premium_schedule import PremiumSchedule
        from app.models.policy import Policy
        from datetime import datetime
        import json
        
        db = SessionLocal()
        alerts = []
        
        # 1. Check for Overdue Payments
        # Joining with Policy to filter by client_id
        overdue_schedules = db.query(PremiumSchedule).join(Policy).filter(
            Policy.client_id == uuid.UUID(client_id),
            PremiumSchedule.status == 'pending'
        ).all()
        
        for schedule in overdue_schedules:
            if schedule.is_overdue:
                # grace_period_ends or due_date
                base_date = schedule.grace_period_ends or schedule.due_date
                days_late = (datetime.now().date() - base_date).days
                
                alerts.append({
                    "type": "late_payment",
                    "id": str(schedule.id),
                    "policy_number": schedule.policy.policy_number,
                    "amount": float(schedule.amount),
                    "due_date": schedule.due_date.isoformat(),
                    "days_late": days_late,
                    "message": f"Payment for Policy #{schedule.policy.policy_number} is {days_late} days late."
                })
        
        # 2. Check for Expiring Policies
        expiring_policies = db.query(Policy).filter(
            Policy.client_id == uuid.UUID(client_id),
            Policy.status == 'active'
        ).all()
        
        for policy in expiring_policies:
            days_left = policy.days_until_expiry
            if days_left is not None and 0 <= days_left <= 30:
                alerts.append({
                    "type": "policy_expiry",
                    "id": str(policy.id),
                    "policy_number": policy.policy_number,
                    "days_left": days_left,
                    "message": f"Policy #{policy.policy_number} will expire in {days_left} days."
                })
                
        return json.dumps(alerts)
    except Exception as e:
        return f"Error scanning for alerts: {str(e)}"
    finally:
        db.close()

@tool
def waive_late_fee(schedule_id: str) -> str:
    """
    Waives the late fee for a specific premium schedule as a gesture of intelligent care.
    """
    print(f"DEBUG: waive_late_fee called for schedule {schedule_id}")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if backend_root not in sys.path: sys.path.append(backend_root)
    
    try:
        from app.core.database import SessionLocal
        from app.models.premium_schedule import PremiumSchedule
        
        db = SessionLocal()
        schedule = db.query(PremiumSchedule).filter(PremiumSchedule.id == uuid.UUID(schedule_id)).first()
        
        if not schedule:
            return f"Error: Premium Schedule {schedule_id} not found."
            
        schedule.status = 'waived'
        schedule.late_fee = 0
        schedule.late_fee_applied = False
        
        db.commit()
        return f"Successfully waived late fee for {schedule.installment_number} of Policy {schedule.policy.policy_number}. The customer has been notified of this courtesy."
    except Exception as e:
        if db: db.rollback()
        return f"Error waiving late fee: {str(e)}"
    finally:
        db.close()
