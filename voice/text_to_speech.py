"""Local text-to-speech utilities using pyttsx3."""
import pyttsx3
from typing import Optional

_ENGINE: Optional[pyttsx3.Engine] = None


def _get_engine() -> pyttsx3.Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = pyttsx3.init()
    return _ENGINE


def speak(text: str) -> None:
    """Speak text using the local TTS engine."""
    engine = _get_engine()
    engine.say(text)
    engine.runAndWait()
