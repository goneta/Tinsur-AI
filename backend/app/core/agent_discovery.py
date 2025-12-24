
import json
import os
from typing import Dict, Optional, List

# Load registry from JSON file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(BASE_DIR, "agent_registry.json")

def load_registry() -> Dict[str, str]:
    """Loads agent registry from JSON and returns name->url map."""
    registry = {}
    try:
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, 'r') as f:
                agents = json.load(f)
                for agent in agents:
                    if agent.get("enabled", True):
                        registry[agent["name"]] = f"http://localhost:{agent['port']}"
        else:
            print(f"Warning: Agent registry not found at {REGISTRY_PATH}")
    except Exception as e:
        print(f"Error loading agent registry: {e}")
    return registry

AGENT_REGISTRY = load_registry()

def get_agent_url(agent_name: str) -> Optional[str]:
    """Retrieves the URL for a given agent by name."""
    # Reload for dev environment to pick up changes without restart, 
    # but for prod we might want to cache. For now, we cache in module scope variable.
    return AGENT_REGISTRY.get(agent_name)

def list_agents() -> Dict[str, str]:
    """Returns the full registry of available agents."""
    return AGENT_REGISTRY
