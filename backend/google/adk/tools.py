
import functools

def tool(func):
    """
    Decorator to mark a function as a tool for the ADK.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@tool
def google_search(query: str) -> str:
    """
    Performs a Google Search.
    Args:
        query: Search query.
    """
    # Mock implementation since we don't have real serper/google search integration details here
    return f"[Google Search Result for '{query}']: found 10 results."
