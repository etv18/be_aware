"""Date-times at the HTTP border.

The app's owner lives in Santo Domingo. Expenses and incomes are stored as that wall-clock time, every
other record as UTC. The controllers hide that difference: they always speak local wall-clock time, in ISO 8601
without an offset ("2026-10-28T12:35:00"). A client that sends an offset ("...Z") is converted too.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

LOCAL = ZoneInfo('America/Santo_Domingo')


def to_local_iso(value, stored_as_utc=True):
    """The stored value as local wall-clock ISO text (None stays None)."""
    if value is None:
        return None
    if value.tzinfo is None and stored_as_utc:
        value = value.replace(tzinfo=timezone.utc)
    if value.tzinfo is not None:
        value = value.astimezone(LOCAL).replace(tzinfo=None)
    return value.replace(microsecond=0).isoformat()


def from_client(value, stored_as_utc=True):
    """What the services should store for a date-time the client sent (None stays None)."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=LOCAL)
    if stored_as_utc:
        return value.astimezone(timezone.utc)
    return value.astimezone(LOCAL).replace(tzinfo=None)
