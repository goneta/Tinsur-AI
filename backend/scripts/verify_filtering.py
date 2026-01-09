import asyncio
import os
import sys

# Setup Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

from backend.agents.a2a_support_agent.tools import search_knowledge_base

async def verify_filtering():
    print("🧪 Verifying Vector DB Metadata Filtering...")
    print("============================================")
    
    query = "What are the rules?" # Very generic query
    
    # 1. Test 'auto' category
    print("\n🔍 Test 1: Category 'auto'")
    result_auto = search_knowledge_base(query, category="auto")
    print(result_auto[:300] + "...")
    
    if "test_policy.pdf" in result_auto and "policy_faq.md" not in result_auto:
        print("✅ SUCCESS: Only 'auto' content returned.")
    else:
        print("❌ FAILURE: Incorrect filtering for 'auto'.")

    # 2. Test 'general' category
    print("\n🔍 Test 2: Category 'general'")
    result_general = search_knowledge_base(query, category="general")
    print(result_general[:300] + "...")
    
    if "policy_faq.md" in result_general and "test_policy.pdf" not in result_general:
        print("✅ SUCCESS: Only 'general' content returned.")
    else:
        print("❌ FAILURE: Incorrect filtering for 'general'.")

    # 3. Test unfiltered
    print("\n🔍 Test 3: No Category (Should return mixed or top matches)")
    result_none = search_knowledge_base(query)
    print(result_none[:300] + "...")
    
    print("✅ Test 3 Complete (Unfiltered).")

if __name__ == "__main__":
    asyncio.run(verify_filtering())
