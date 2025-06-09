import whisper
from tempfile import NamedTemporaryFile
from typing import Union

model = whisper.load_model("base")

def transcribe_audio(data: Union[bytes, str]) -> str:
    """Transcribe audio bytes or a file path using Whisper."""
    if isinstance(data, bytes):
        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(data)
            tmp.flush()
            path = tmp.name
    else:
        path = data
    result = model.transcribe(path)
    return result.get("text", "").strip()
