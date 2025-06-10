"""Very simple intent parser using regex patterns."""
import re
from typing import Dict, Tuple

_INTENTS = {
    "set_reminder": re.compile(r"remind me to (?P<title>.+) at (?P<time>.+)", re.I),
    "list_snacks": re.compile(r"what.*snacks", re.I),
    "train_status": re.compile(r"train.*(delayed|status)", re.I),
    "turn_on_light": re.compile(r"turn on the (?P<device>.+)", re.I),
}


def parse_intent(text: str) -> Tuple[str, Dict[str, str]]:
    """Return intent name and extracted parameters."""
    for name, pattern in _INTENTS.items():
        match = pattern.search(text)
        if match:
            return name, {k: v for k, v in match.groupdict().items() if v}
    return "unknown", {}
