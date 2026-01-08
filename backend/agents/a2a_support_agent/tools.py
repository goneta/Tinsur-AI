import os
import sys
import chromadb
import uuid
import google.generativeai as genai
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.models.ticket import Ticket

def search_knowledge_base(query: str) -> str:
    """
    Search the Tinsur.AI policy knowledge base for relevant information 
    to answer the user's question.
    """
    print(f"DEBUG: search_knowledge_base called with query: {query}")
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

        results = collection.query(
            query_embeddings=[emb_result['embedding']],
            n_results=2
        )
        
        if results['documents'] and results['documents'][0]:
            docs = results['documents'][0]
            return "\n\n".join(docs)
        
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
