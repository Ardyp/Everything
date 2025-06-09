import re
from datetime import datetime, timedelta

def parse_intent(text: str):
    """Very naive rule-based NLU to map text to API calls."""
    t = text.lower()
    if "remind me" in t:
        return {
            "method": "POST",
            "path": "/reminder",
            "payload": {
                "title": "Call John",
                "due_date": (datetime.now() + timedelta(hours=1)).isoformat(),
            },
            "success_message": "Reminder created"
        }
    if "snack" in t:
        return {
            "method": "POST",
            "path": "/inventory/update",
            "payload": {
                "name": "chips",
                "category": "snacks",
                "quantity": 1,
                "unit": "bags"
            },
            "success_message": "Inventory updated"
        }
    if "gym" in t:
        return {
            "method": "POST",
            "path": "/health/gym",
            "payload": {},
            "success_message": "Gym visit logged"
        }
    if "house" in t or "home status" in t:
        return {"method": "GET", "path": "/status", "success_message": "Here is the home status"}
    if "commute" in t:
        return {"method": "GET", "path": "/commute/summary", "success_message": "Here is your commute"}
    return None
