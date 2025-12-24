from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .cymbal_agent_wrapper import bank_agent_wrapper


class AdvisorsSummary(BaseModel):
    """Structured output for Advisors"""

    advisors: list[str] = Field(
        description="List of advisors with the availability sorted by advisor_type "
    )
    meetings: list[str] = Field(description="List of user's meeting")


retriever_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="Advisors_retriever",
    tools=[AgentTool(bank_agent_wrapper)],
    description="An agent that retrieves the bank's advisors and user meetings",
    instruction="""
    You are a helpful financial assistant. Your goal is to gather user's meetings and list of advisors 
    
    **Phase 1: Get list of meetings**
    Call the bank_agent_wrapper tool with the query "List my meetings." to get the user's scheduled meetings.

    **Phase 2: Get list of bank's advisors**
    Call the bank_agent_wrapper tool with the query "List the advisors." to get the advisors of the bank.
    
    **Phase 3: Get User Profile**
    Call the bank_agent_wrapper tool with the query "Get my user profile" to get the user's profile information
    
    Combine the meeting data, advisor data and user profile information in your response for the next agent to use.
    """,
    output_key="Advisors_data",
)

formatting_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="Advisors_formatter",
    description="Analyzes user's advisor and meeting data and generates structured summary",
    instruction="""
    You are an expert financial analyst. Using the user meeting data, analyst data and user profile from the 'Advisors_data' state key, 
    analyze the information and provide structured insights.

    **Your Task:**
    1. **Your Meetings**: List the user's scheduled meetings (format: "Date - Time - Advisor - Purpose")
    2. **Your Advisors**: List of your bank's advisors with availability sorted by advisor_type
   
    **CRITICAL CONSTRAINTS:**
    - You must return a structured JSON response that matches the AdvisorsSummary schema exactly
    """,
    output_schema=AdvisorsSummary,
    output_key="Advisors_summary",
)


advisors_snapshot_workflow = SequentialAgent(
    name="Advisors_snapshot_pipeline",
    description="Executes a pre-decided pipeline. It retrieves advisor data and meeting data , then generates structured  insights.",
    sub_agents=[
        retriever_agent,
        formatting_agent,
    ],
)

root_agent = advisors_snapshot_workflow
