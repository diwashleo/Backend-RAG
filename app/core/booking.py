import re
from datetime import datetime, date, time
from typing import Optional, Tuple
from dateutil import parser as dateparser

# Booking Patterns
BOOKING_KEYWORDS = re.compile(r"\b(book|schedule|set up|reserve|arrange)\b.*\b(interview|meeting)\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

NAME_PATTERNS = [
    re.compile(r"(?:my name is|i am|i'm)\s+([A-Za-z][A-Za-z\s.'-]{1,60})", re.IGNORECASE),
    re.compile(r"name[:\-]\s*([A-Za-z][A-Za-z\s.'-]{1,60})", re.IGNORECASE)
]

def is_booking_intent(text: str) -> bool:
    return bool(BOOKING_KEYWORDS.search(text))

def parse_date_and_time(text: str) -> Tuple[Optional[date], Optional[time]]:
    sentinel = datetime(2025, 1, 1, 0, 0)
    try: 
        parsed_dt = dateparser.parse(text, fuzzy=True, default=sentinel)
    except Exception:
        return None, None
    
    if parsed_dt is None:
        return None, None

    if parsed_dt.tzinfo:
        parsed_dt = parsed_dt.replace(tzinfo=None)

    has_date = (
        parsed_dt.year != sentinel.year or parsed_dt.month != sentinel.month or parsed_dt.day != sentinel.day
    )
    has_time = (parsed_dt.hour != sentinel.hour or parsed_dt.minute != sentinel.minute)

    event_date = parsed_dt.date() if has_date else None
    event_time = time(parsed_dt.hour, parsed_dt.minute) if has_time else None

    return event_date, event_time

def extract_booking_slots(text: str):
    name = None
    for pattern in NAME_PATTERNS:
        match = pattern.search(text)
        if match:
            raw_name = match.group(1).strip()
            name = re.split(r"\band\b|\bemail\b", raw_name, flags=re.IGNORECASE)[0].strip()
            break
    
    email_match = EMAIL_RE.search(text)
    email = email_match.group(0) if email_match else None

    event_date, event_time = parse_date_and_time(text)

    return name, email, event_date, event_time