from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Request
from httpx import AsyncClient
from .speech_to_text import transcribe_audio
from .text_to_speech import speak
from utils.nlu_parser import parse_intent

router = APIRouter()

@router.post("/")
async def voice_command(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Transcribe audio and route to the appropriate agent."""
    audio_bytes = await file.read()
    text = transcribe_audio(audio_bytes)

    intent = parse_intent(text)
    if not intent:
        background_tasks.add_task(speak, "Sorry, I didn't understand.")
        return {"text": text, "response": "Unrecognized command"}

    async with AsyncClient(app=request.app, base_url="http://app") as client:
        resp = await client.request(intent["method"], intent["path"], json=intent.get("payload"))
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())
    data = resp.json()

    message = intent.get("success_message", "Done")
    if isinstance(data, dict) and "message" in data:
        message = data["message"]

    background_tasks.add_task(speak, message)
    return {"text": text, "response": data}
