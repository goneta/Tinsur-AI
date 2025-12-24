from typing import List

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .cymbal_agent_wrapper import bank_agent_wrapper


class SpendingSummary(BaseModel):
    """Structured output for spending analysis"""

    activities: List[str] = Field(description="List of 5 most recent transactions")
    income: float = Field(description="Total income amount from transactions")
    expenses: float = Field(description="Total expenses amount from transactions")
    insights: str = Field(
        description="Financial insights based on user goals and spending patterns"
    )


retriever_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="spending_retriever",
    description="An agent that retrieves user transaction data and profile information for the requested period. ",
    instruction="""
    You are a helpful financial assistant. Your goal is to gather comprehensive spending and profile data.
    
    **Phase 1: Get Transaction Data**
    Call the cymbal_agent tool with the query "List my recent transactions." to get the user's transaction history.
    
    **Phase 2: Get User Profile**
    Call the cymbal_agent tool with the query "Get my user profile" to get the user's profile information including their financial goals.
    
    Combine both the transaction data and user profile information in your response for the next agent to use.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="spending_data",
)

formatting_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="spending_formatter",
    description="Analyzes spending data and generates structured financial insights",
    instruction="""
    You are an expert financial analyst. Using the spending data and user profile from the 'spending_data' state key, 
    analyze the information and provide structured insights.

    **Your Task:**
    1. **Activities**: List the 5 most recent transactions (format: "Date - Merchant - Amount")
    2. **Income**: Calculate total income from transactions (look for payrolls, salary deposits, refunds, etc.)
    3. **Expenses**: Calculate total expenses from transactions (purchases, bills, rent, groceries, etc.)
    4. **Insights**: Analyze spending patterns against the user's goals from their profile. Provide actionable insights about their financial behavior, potential savings opportunities, or goal alignment.

    **CRITICAL CONSTRAINTS:**
    - You must return a structured JSON response that matches the SpendingSummary schema exactly
    - Base income/expense calculations on transaction types and amounts 
    - Make insights specific and actionable based on the user's stated goals
    """,
    output_schema=SpendingSummary,
    output_key="spending_summary",
)


spending_snapshot_workflow = SequentialAgent(
    name="spending_snapshot_pipeline",
    description="Executes a pre-decided pipeline. It retrieves transaction data and user profile, then generates structured financial insights.",
    sub_agents=[
        retriever_agent,
        formatting_agent,
    ],
)

root_agent = spending_snapshot_workflow
