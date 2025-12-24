from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .cymbal_agent_wrapper import bank_agent_wrapper


class PerksSummary(BaseModel):
    """Structured output for perks analysis"""

    activities: list[str] = Field(description="List of user benefits by category")
    partners: list[str] = Field(description="List of bank's partners")
    insights: str = Field(description="Financial insights based on user's benefits")


retriever_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="perks_retriever",
    description="An agent that retrieves the bank's partners and user benefits for the requested period",
    instruction="""
    You are a helpful financial assistant. Your goal is to gather comprehensive user benefits data.
    
    **Phase 1: Get Benefits Data**
    Call the cymbal_agent tool with the query "List my benefits." to get the user's benefits.

    **Phase 2: Get Bank Partners**
    Call the cymbal_agent tool with the query "List the bank partners." to get the partners of the bank.
    
    **Phase 2: Get User Profile**
    Call the cymbal_agent tool with the query "Get my user profile" to get the user's profile information including their financial goals.
    
    Combine both the benefits data and user profile information in your response for the next agent to use.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="perks_data",
)

formatting_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="perks_formatter",
    description="Analyzes user's benefits data and generates structured financial insights",
    instruction="""
    You are an expert financial analyst. Using the user benefits data and user profile from the 'perks_data' state key, 
    analyze the information and provide structured insights.

    **Your Task:**
    1. **Your Benefits**: List the user benefits category wise(format: "Name - Category - Benefit Type - Benefit Value")
    2. **Your Bank partners**: List of your bank's partners
   
    **CRITICAL CONSTRAINTS:**
    - You must return a structured JSON response that matches the PerksSummary schema exactly
    """,
    output_schema=PerksSummary,
    output_key="perks_summary",
)


perks_snapshot_workflow = SequentialAgent(
    name="perks_snapshot_pipeline",
    description="Executes a pre-decided pipeline. It retrieves benefits data and user profile, then generates structured financial insights.",
    sub_agents=[
        retriever_agent,
        formatting_agent,
    ],
)

root_agent = perks_snapshot_workflow
