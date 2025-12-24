from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .cymbal_agent_wrapper import bank_agent_wrapper


class PortfolioSummary(BaseModel):
    """Structured output for portfolio analysis"""

    debts: list[str] = Field(description="List of user debts")
    investments: list[str] = Field(description="List of user investments")
    networth: list[str] = Field(description="List of user networth")
    cashflow: list[str] = Field(description="List of user cashflow")
    average_cashflow: list[str] = Field(description="List of user average_cashflow")
    insights: str = Field(
        description="Financial insights based on user's debts, investments, networth, cashflow, average_cashflow and profile"
    )


retriever_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="portfolio_retriever",
    description="An agent that retrieves user portfolio data and profile information",
    instruction="""
    You are a helpful financial assistant. Your goal is to gather comprehensive portfolio data.
    
    **Phase 1: Get Portfolio Data**
    Call the cymbal_agent tool with the query "List my portfolio data including debts, investments, and financial overview." to get the user's portfolio information.
    
    **Phase 2: Get User Profile**
    Call the cymbal_agent tool with the query "Get my user profile" to get the user's profile information including their financial goals.
    
    Combine both the portfolio data and user profile information in your response for the next agent to use.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="portfolio_data",
)

formatting_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="portfolio_formatter",
    description="Analyzes user's portfolio data and generates structured financial insights",
    instruction="""
    You are an expert financial analyst. Using the portfolio data and user profile from the 'portfolio_data' state key, 
    analyze the information and provide structured insights.

    **Your Task:**
    1. **Debts**: List user's debts (format: "Debt Type - Amount - Interest Rate")
    2. **Investments**: List user's investments (format: "Investment Type - Amount - Performance")
    3. **Net Worth**: List net worth calculations (format: "Assets - Liabilities = Net Worth")
    4. **Cashflow**: List cashflow items (format: "Income Source/Expense - Amount - Frequency")
    5. **Average Cashflow**: List average cashflow calculations (format: "Monthly Average - Yearly Projection")
    6. **Insights**: Analyze portfolio health, investment performance, debt management, and alignment with user goals from their profile.

    **CRITICAL CONSTRAINTS:**
    - You must return a structured JSON response that matches the PortfolioSummary schema exactly
    - Base calculations on available portfolio data
    - Make insights specific and actionable based on the user's stated goals and financial position
    """,
    output_schema=PortfolioSummary,
    output_key="portfolio_summary",
)


portfolio_snapshot_workflow = SequentialAgent(
    name="portfolio_snapshot_pipeline",
    description="Executes a pre-decided pipeline. It retrieves portfolio data and user profile, then generates structured financial insights.",
    sub_agents=[
        retriever_agent,
        formatting_agent,
    ],
)

root_agent = portfolio_snapshot_workflow
