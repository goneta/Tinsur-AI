from contextvars import ContextVar
from typing import Optional

# Global context variable for the Google API key, scoped to the current asynchronous request.
google_api_key_var: ContextVar[Optional[str]] = ContextVar("google_api_key", default=None)
