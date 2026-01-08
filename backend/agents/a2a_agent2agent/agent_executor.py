from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from app.core.agent_client import AgentClient
import json

class AgentToAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="connector_agent",
            model="gemini-2.0-flash",
            description="Agent that acts as a router to other specialist agents.",
            instruction="""
            You are a Connector Agent for InsurSaaS.
            Your role is to route user requests to the appropriate specialist agent.
            
            Available Agents:
            - quote_agent: For getting insurance quotes, premium calculations.
            - claims_agent: For reporting accidents, checking claim status.
            - policy_agent: For viewing policy details, renewals.
            - support_agent: For general questions, technical support.
            
            When a user sends a message:
            1. Analyze the intent.
            2. Decide which agent can best handle it.
            3. Return a JSON object with the routing decision.
            
            Output Format:
            ```json
            {
                "target_agent": "agent_name_without_suffix", 
                "reasoning": "Brief explanation"
            }
            ```
            Example: {"target_agent": "quote", "reasoning": "User wants a car insurance quote"}
            
            If the request is general (e.g., "Hello", "Who are you?"), return {"target_agent": null, "reasoning": "General conversation"} and answer the user directly in a separate text.
            """,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        try:
            # 1. Extract User Input
            user_input = "Hello"
            if context.events:
                 for event in reversed(context.events):
                     if event.type == "user_text_message":
                         user_input = event.text
                         break
            
            # 2. Determine Routing with Gemini
            # We ask the agent to return the JSON routing decision
            routing_prompt = f"""
            User Input: "{user_input}"
            
            Decide where to route this message based on the available agents. 
            Return the JSON decision.
            """
            
            llm_response = await self.agent.run(routing_prompt)
            
            # 3. Parse Decision
            target_agent = None
            try:
                # Clean and parse JSON
                cleaned_json = llm_response.replace("```json", "").replace("```", "").strip()
                if "{" in cleaned_json:
                    cleaned_json = cleaned_json[cleaned_json.find("{"):cleaned_json.rfind("}")+1]
                
                decision = json.loads(cleaned_json)
                target_agent = decision.get("target_agent")
            except Exception as e:
                print(f"Routing Parse Error: {e}")
                # Fallback: simple keyword match
                if "quote" in user_input.lower(): target_agent = "quote"
                elif "claim" in user_input.lower(): target_agent = "claims"
            
            # 4. Route or Reply
            if target_agent:
                # Append _agent suffix if not present (convention varies, but AgentClient expects registry name)
                # Assuming registry uses "quote_agent", "claims_agent"
                agent_name = f"{target_agent}_agent" 
                
                event_queue.enqueue_event(new_agent_text_message(f"Connecting you to the {target_agent} specialist..."))
                
                client = AgentClient()
                # Pass context if needed
                agent_response = await client.send_message(
                    agent_name=agent_name,
                    message=user_input,
                    context=context.metadata
                )
                
                # Process response
                if "messages" in agent_response:
                    for msg in agent_response["messages"]:
                        text = msg.get("content") or msg.get("text")
                        if text:
                            event_queue.enqueue_event(new_agent_text_message(text))
                elif "error" in agent_response:
                     event_queue.enqueue_event(new_agent_text_message(f"Error connecting to agent: {agent_response['error']}"))
                else:
                     event_queue.enqueue_event(new_agent_text_message(f"Received empty response from {agent_name}."))

            else:
                # Handle locally (General Chat)
                # The LLM might have already generated a text response if we asked it to, 
                # but we limited it to JSON. Let's ask again for a collection response if needed, 
                # or just use a standard greeting.
                reply = await self.agent.run(f"Reply to this user as a helpful connector agent. User: {user_input}")
                event_queue.enqueue_event(new_agent_text_message(reply))

        except Exception as e:
            print(f"Connector Agent Error: {e}")
            event_queue.enqueue_event(new_agent_text_message("I'm sorry, I'm having trouble connecting to the network right now."))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
