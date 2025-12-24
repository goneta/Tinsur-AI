from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool

from .cymbal_agent_wrapper import bank_agent_wrapper

retriever_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="spending_retriever",
    description="Research is everything regarding the users current spending",
    instruction="""
    You are an expert report architect. Using the research topic and the plan from the 'research_plan' state key, design a logical structure for the final report.
    Note: Ignore all the tag nanes ([MODIFIED], [NEW], [RESEARCH], [DELIVERABLE]) in the research plan.
    Your task is to create a markdown outline with 4-6 distinct sections that cover the topic comprehensively without overlap.
    You can use any markdown format you prefer, but here's a suggested structure:
    # Section Name
    A brief overview of what this section covers
    Feel free to add subsections or bullet points if needed to better organize the content.
    Make sure your outline is clear and easy to follow.
    Do not include a "References" or "Sources" section in your outline. Citations will be handled in-line.
    """,
    output_key="spending_data",
)

chart_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="spending_chart_agent",
    description="Create a chart of the users spending",
    instruction="""
    You are an expert chart architect. Using the spending data from the 'spending_data' state key, create a chart of the users spending.
    """,
    tools=[AgentTool(bank_agent_wrapper)],
    output_key="spending_chart",
)


spending_snapshot_workflow = SequentialAgent(
    name="research_pipeline",
    description="Executes a pre-approved research plan. It performs iterative research, evaluation, and composes a final, cited report.",
    sub_agents=[
        retriever_agent,
        chart_agent,
    ],
)

root_agent = spending_snapshot_workflow
