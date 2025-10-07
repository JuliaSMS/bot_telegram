from datetime import datetime, timedelta


def today_date_str():
    return datetime.utcnow().date().isoformat()


def days_between_dates(a: str, b: str) -> int:
    da = datetime.fromisoformat(a).date()
    db = datetime.fromisoformat(b).date()
    return (db - da).days
