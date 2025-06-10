"""Voice command processing pipeline."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from .speech_to_text import transcribe_audio_bytes
from .text_to_speech import speak
from nlu.parser import parse_intent
import logging

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/command")
async def process_voice_command(file: UploadFile = File(...)):
    """Accept an audio file, process it, and respond via TTS."""
    audio = await file.read()
    try:
        transcript = transcribe_audio_bytes(audio)
    except Exception as e:
        logging.exception("STT failed")
        raise HTTPException(status_code=500, detail=f"STT error: {e}")

    intent, params = parse_intent(transcript)
    # TODO: Route to specific agent based on detected intent
    response_text = f"Recognized intent {intent}"

    # Speak the response back to the user
    try:
        speak(response_text)
    except Exception:
        logging.exception("TTS failed")

    return {"transcript": transcript, "intent": intent, "params": params}
