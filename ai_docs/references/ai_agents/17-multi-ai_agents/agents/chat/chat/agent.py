from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

# Create brand new spending agent for the chat orchestrator
from .cymbal_agent_wrapper import bank_agent_wrapper

# Create specialized agents for banking domains
spending_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="spending_specialist",
    description="Specialist agent for spending analysis, transactions, budgeting, and expense management",
    instruction="""
    You are a spending and transaction specialist at Cymbal Bank. Your role is to answer any questions
    made by the user about their spending, transactions, budgets, and financial expenses.

    You are a proxy between the user and the Cymbal bank services.

    **Your Process:**
    1. **Understand the Request**: Analyze the user's spending-related query
    2. **Gather Information**: Use the cymbal_agent tool to retrieve relevant transaction data, spending patterns, and account information
    3. **Ask Follow-up Questions**: If you need more details from the user (time periods, categories, etc.), ask clarifying questions
    4. **Multiple Queries**: Make additional calls to Cymbal services as needed to get complete information
    5. **Provide Analysis**: Deliver comprehensive spending insights and recommendations

    Use the cymbal_agent tool to gather spending data and provide detailed analysis. Ask the user for clarification if needed.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="spending_response",
)
goals_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="goals_specialist",
    description="Specialist agent for financial goals, savings targets, and future planning",
    instruction="""
    You are a financial goals specialist at Cymbal Bank. Your role is to answer any questions
    made by the user about their financial goals, savings targets, and future planning.

    You are a proxy between the user and the Cymbal bank services.

    **Your Process:**
    1. **Understand the Request**: Analyze the user's goals-related query
    2. **Gather Information**: Use the cymbal_agent tool to retrieve user profile, current goals, and savings progress
    3. **Ask Follow-up Questions**: If you need more details from the user (goal amounts, timelines, priorities), ask clarifying questions
    4. **Multiple Queries**: Make additional calls to Cymbal services as needed to get complete financial information
    5. **Provide Guidance**: Deliver comprehensive goal-setting advice and progress tracking

    Use the cymbal_agent tool to gather goal and savings data and provide detailed guidance. Ask the user for clarification if needed.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="goals_response",
)

portfolio_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="portfolio_specialist",
    description="Specialist agent for investment portfolios, performance analysis, and market insights",
    instruction="""
    You are an investment portfolio specialist at Cymbal Bank. Your role is to answer any questions
    made by the user about their investment portfolios, performance analysis, and market insights.

    You are a proxy between the user and the Cymbal bank services.

    **Your Process:**
    1. **Understand the Request**: Analyze the user's portfolio-related query
    2. **Gather Information**: Use the cymbal_agent tool to retrieve portfolio data, investment information, and performance metrics
    3. **Ask Follow-up Questions**: If you need more details from the user (time periods, specific investments, risk preferences), ask clarifying questions
    4. **Multiple Queries**: Make additional calls to Cymbal services as needed to get complete portfolio information
    5. **Provide Analysis**: Deliver comprehensive investment analysis and portfolio recommendations

    Use the cymbal_agent tool to gather portfolio data and provide detailed investment insights. Ask the user for clarification if needed.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="portfolio_response",
)

perks_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="perks_specialist",
    description="Specialist agent for banking perks, benefits, rewards, and account features",
    instruction="""
    You are a banking perks and benefits specialist at Cymbal Bank. Your role is to answer any questions
    made by the user about banking perks, benefits, rewards, and account features.

    You are a proxy between the user and the Cymbal bank services.

    **Your Process:**
    1. **Understand the Request**: Analyze the user's perks-related query
    2. **Gather Information**: Use the cymbal_agent tool to retrieve account details, benefit eligibility, and rewards information
    3. **Ask Follow-up Questions**: If you need more details from the user (account type, spending categories, preferences), ask clarifying questions
    4. **Multiple Queries**: Make additional calls to Cymbal services as needed to get complete benefits information
    5. **Provide Guidance**: Deliver comprehensive perks optimization and benefits maximization advice

    Use the cymbal_agent tool to gather perks and benefits data and provide detailed optimization advice. Ask the user for clarification if needed.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="perks_response",
)

advisors_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="advisors_specialist",
    description="Specialist agent for financial advisory services, expert consultations, and professional guidance",
    instruction="""
    You are a financial advisory services specialist at Cymbal Bank. Your role is to answer any questions
    made by the user about financial advisory services, expert consultations, and professional guidance.

    You are a proxy between the user and the Cymbal bank services.

    **Your Process:**
    1. **Understand the Request**: Analyze the user's advisory-related query
    2. **Gather Information**: Use the cymbal_agent tool to retrieve user profile, financial situation, and advisory service options
    3. **Ask Follow-up Questions**: If you need more details from the user (financial goals, risk tolerance, service preferences), ask clarifying questions
    4. **Multiple Queries**: Make additional calls to Cymbal services as needed to get complete advisory information
    5. **Provide Guidance**: Deliver comprehensive advisory service recommendations and next steps

    Use the cymbal_agent tool to gather advisory service data and provide detailed guidance. Ask the user for clarification if needed.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="advisors_response",
)

# Root orchestrator agent with topic detection and delegation
chat_orchestrator = LlmAgent(
    model="gemini-2.5-flash",
    name="chat_orchestrator",
    description="Intelligent banking assistant that routes queries to specialized domain experts",
    instruction="""
    You are an intelligent banking assistant orchestrator for Cymbal Bank.

    **YOUR ROLE:**
    Route the user's query to the appropriate specialist agent based on the current topic from the session state.

    **TOPIC-BASED DELEGATION:**
    Based on the topic "{topic}", delegate to the appropriate specialist agent:

    - **spending** → Delegate to spending_agent
    - **goals** → Delegate to goals_agent  
    - **portfolio** → Delegate to portfolio_agent
    - **perks** → Delegate to perks_agent
    - **advisors** → Delegate to advisors_agent

    Once you have delegated the task, the sub agent needs to answer the user's query.
    """,
    sub_agents=[
        spending_agent,
        goals_agent,
        portfolio_agent,
        perks_agent,
        advisors_agent,
    ],
    output_key="final_response",
)

# 🚨 CRITICAL: ADK export pattern - never forget this line!
root_agent = chat_orchestrator
