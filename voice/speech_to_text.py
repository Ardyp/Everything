import os
import json
import io
import wave
from vosk import Model, KaldiRecognizer
from typing import Optional

MODEL_PATH = os.getenv("VOSK_MODEL", "model")

_model_cache: Optional[Model] = None


def _load_model() -> Model:
    global _model_cache
    if _model_cache is None:
        if not os.path.isdir(MODEL_PATH):
            raise RuntimeError(f"Vosk model not found at {MODEL_PATH}")
        _model_cache = Model(MODEL_PATH)
    return _model_cache


def transcribe_audio(audio_bytes: bytes) -> str:
    model = _load_model()
    with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
        rec = KaldiRecognizer(model, wf.getframerate())
        result = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result.append(res.get("text", ""))
        res = json.loads(rec.FinalResult())
        result.append(res.get("text", ""))
    return " ".join(result).strip()
