from datetime import datetime, timezone


def now_utc() -> datetime:
    """Получить текущее время в UTC"""
    return datetime.now(timezone.utc)