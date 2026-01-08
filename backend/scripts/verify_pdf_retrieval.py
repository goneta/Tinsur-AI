import os
import sys

# Setup paths
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(backend_root)
sys.path.append(os.path.join(backend_root, "agents/a2a_support_agent"))

from tools import search_knowledge_base

def verify_pdf_rag():
    print("🧪 Verifying PDF RAG Retrieval...")
    
    # Query that is specifically in the test_policy.pdf
    query = "What are the storage requirements for vintage cars?"
    print(f"❓ Query: {query}")
    
    result = search_knowledge_base(query)
    
    print("\n📚 Retrieved Context:")
    print(result)
    
    if "locked garage" in result.lower():
        print("\n✅ SUCCESS: Correct context retrieved from PDF!")
    else:
        print("\n❌ FAILURE: Could not find PDF content in retrieval.")

if __name__ == "__main__":
    verify_pdf_rag()
