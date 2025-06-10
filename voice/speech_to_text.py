"""Offline speech-to-text utilities using Vosk."""
import io
import json
import os
import wave
from typing import Optional
from vosk import Model, KaldiRecognizer

# Path to the Vosk model can be configured via environment variable
_MODEL: Optional[Model] = None
MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")


def _get_model() -> Model:
    """Load Vosk model lazily."""
    global _MODEL
    if _MODEL is None:
        _MODEL = Model(MODEL_PATH)
    return _MODEL


def transcribe_audio_bytes(data: bytes) -> str:
    """Transcribe WAV audio bytes to text."""
    wf = wave.open(io.BytesIO(data), "rb")
    rec = KaldiRecognizer(_get_model(), wf.getframerate())
    text = ""
    while True:
        chunk = wf.readframes(4000)
        if not chunk:
            break
        if rec.AcceptWaveform(chunk):
            result = json.loads(rec.Result())
            text += result.get("text", "") + " "
    final = json.loads(rec.FinalResult())
    text += final.get("text", "")
    return text.strip()
