from datetime import UTC, datetime


def utcnow() -> datetime:
    """Naive UTC for compatibility with the existing MySQL TIMESTAMP columns."""
    return datetime.now(UTC).replace(tzinfo=None)
