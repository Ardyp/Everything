import re
from typing import Dict

# Very basic intent parser
_PATTERNS = {
    "add_reminder": re.compile(r"remind me to (?P<item>.+)", re.I),
    "get_weather": re.compile(r"weather", re.I),
}


def parse_intent(text: str) -> Dict[str, str]:
    for intent, pattern in _PATTERNS.items():
        match = pattern.search(text)
        if match:
            return {"intent": intent, **match.groupdict()}
    return {"intent": "unknown", "text": text}
