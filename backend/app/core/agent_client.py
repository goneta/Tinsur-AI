
import requests
import os
from typing import Optional, Dict, Any
from .agent_discovery import get_agent_url
import logging
import asyncio

logger = logging.getLogger(__name__)

class AgentClient:
    def __init__(self):
        self.api_key = os.getenv("A2A_INTERNAL_API_KEY", "super-secret-a2a-key")
        self.timeout = 30.0 # seconds

    async def send_message(self, agent_name: str, message: str, context: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends a text message to a specific agent and awaits the response.
        Uses requests wrapped in asyncio.to_thread to avoid blocking event loop.
        """
        return await asyncio.to_thread(self._send_message_sync, agent_name, message, context, api_key)

    def _send_message_sync(self, agent_name: str, message: str, context: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        base_url = get_agent_url(agent_name)
        if not base_url:
            raise ValueError(f"Agent '{agent_name}' not found in registry.")

        url = f"{base_url}/send-message"
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }
        
        payload = {
            "message": {
                 "type": "user_text_message",
                 "text": message
            },
            "context": {**(context or {}), "google_api_key": api_key}
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            # Never fabricate a success message here: pretending an action
            # happened (e.g. "claim filed") is worse than an honest error.
            # Callers treat {"error": ...} as a signal to use their own
            # fallback (e.g. direct LLM call in the chat endpoint).
            logger.warning(f"Agent {agent_name} unreachable at {url}.")
            return {"error": f"Agent {agent_name} is unreachable"}
        except requests.HTTPError as e:
            logger.error(f"Error calling agent {agent_name}: {e.response.text}")
            return {"error": f"Agent {agent_name} returned error: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Failed to communicate with agent {agent_name}: {str(e)}")
            return {"error": f"Communication failure: {str(e)}"}
