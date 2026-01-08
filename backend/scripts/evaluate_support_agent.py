import asyncio
import os
import sys
import json
import google.generativeai as genai

# Setup Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

from backend.agents.a2a_support_agent.agent_executor import SupportAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

class MockEvent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

async def get_judge_score(question, expected, actual):
    """Uses Gemini as a judge to score the actual response against the expected one."""
    from app.core.config import settings
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        return 0, "MISSING_API_KEY"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are an impartial judge evaluating the output of an AI Support Agent.
    
    Question: {question}
    Expected Key Information: {expected}
    Actual Agent Response: {actual}
    
    Evaluate Based on:
    1. Accuracy: Does it contain the expected key information?
    2. Correctness: Does it avoid hallucinations?
    3. Proper Tool Use: If it's an escalation, did it create a ticket?
    
    Return ONLY a JSON object:
    {{"score": 1-5, "rationale": "short explanation"}}
    
    Scores:
    1: Completely wrong or irrelevant.
    3: Correct information but poorly phrased or missed minor details.
    5: Perfect accuracy and professional tone.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean potential markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        data = json.loads(text)
        return data.get("score", 0), data.get("rationale", "N/A")
    except Exception as e:
        return 0, f"Judge Error: {e}"

async def run_evaluation():
    print("🏆 Tinsur.AI Support Agent - Quality Evaluation")
    print("===============================================")
    
    golden_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/eval_golden_set.json"))
    with open(golden_path, "r", encoding="utf-8") as f:
        golden_set = json.load(f)
        
    executor = SupportAgentExecutor()
    results = []
    
    client_id = "bf448f88-fde2-48f4-97eb-ba8d189b6c4e" 
    company_id = "1e47dd3a-413a-4257-9114-fd8eed222908"

    for item in golden_set:
        print(f"\n📝 Testing [{item['id']}] Category: {item['category']}")
        print(f"   Q: {item['question']}")
        
        context = RequestContext(
            events=[MockEvent(type="user_text_message", text=item['question'])],
            metadata={
                "google_api_key": os.getenv("GOOGLE_API_KEY"),
                "client_id": client_id,
                "company_id": company_id
            }
        )
        event_queue = EventQueue()
        
        try:
            await executor.execute(context, event_queue)
            actual_text = ""
            if event_queue.events:
                # SupportAgent usually sends one response
                evt = event_queue.events[0]
                actual_text = evt.get("text", "") if isinstance(evt, dict) else getattr(evt, "text", "")
            
            score, rationale = await get_judge_score(item['question'], item['expected'], actual_text)
            
            print(f"   Score: {score}/5")
            print(f"   Rationale: {rationale}")
            
            results.append({
                "id": item['id'],
                "score": score,
                "category": item['category']
            })
            
        except Exception as e:
            print(f"   ❌ Execution Failed: {e}")

    # Final Summary
    print("\n\n📊 Final Evaluation Summary")
    print("===========================")
    if results:
        avg_score = sum(r['score'] for r in results) / len(results)
        print(f"Total Questions: {len(results)}")
        print(f"Average Quality Score: {avg_score:.2f}/5.0")
        
        # Breakdown by category
        cats = set(r['category'] for r in results)
        for cat in cats:
            cat_results = [r for r in results if r['category'] == cat]
            cat_avg = sum(r['score'] for r in cat_results) / len(cat_results)
            print(f" - {cat}: {cat_avg:.2f}/5.0")
    else:
        print("No results to report.")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
