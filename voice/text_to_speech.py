import pyttsx3
from typing import Optional
import io

_engine: Optional[pyttsx3.Engine] = None


def _init_engine() -> pyttsx3.Engine:
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
    return _engine


def synthesize_speech(text: str) -> bytes:
    engine = _init_engine()
    with io.BytesIO() as buffer:
        engine.save_to_file(text, buffer)
        engine.runAndWait()
        return buffer.getvalue()
