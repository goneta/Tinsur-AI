"""
Time helpers.
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Timezone-aware UTC now for database defaults."""
    return datetime.now(timezone.utc)


def utcnow_date():
    """UTC date for Date columns."""
    return datetime.now(timezone.utc).date()
