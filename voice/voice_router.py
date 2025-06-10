from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from nlu.parser import parse_intent
from .speech_to_text import transcribe_audio
from .text_to_speech import synthesize_speech
import io

from agents.life_organizer.main import router as life_router  # Example

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/command")
async def voice_command(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    try:
        text = transcribe_audio(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    intent = parse_intent(text)
    response_text = f"Heard: {text}. Intent: {intent['intent']}"
    audio_out = synthesize_speech(response_text)
    return StreamingResponse(io.BytesIO(audio_out), media_type="audio/wav")
