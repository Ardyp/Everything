from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
import json
from datetime import datetime

import openai
from gtts import gTTS

router = APIRouter(prefix="/voice", tags=["voice"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai.Client(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@router.post("/command")
async def voice_command(audio: UploadFile = File(...)):
    """Accept audio, transcribe it, resolve intent, and return TTS audio."""
    if openai_client is None:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Save uploaded audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        audio_path = tmp.name

    try:
        with open(audio_path, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )
        text = transcription.text
    except Exception as e:
        os.remove(audio_path)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

    # Use OpenAI ChatGPT to generate a simple JSON instruction
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Convert the user's command into a JSON instruction.\n"
                    "Actions: update_device or create_reminder.\n"
                    "For update_device, return: {\"action\": \"update_device\", \"device_id\": <id>, \"status\": <on/off>}\n"
                    "For create_reminder, return: {\"action\": \"create_reminder\", \"title\": <title>, \"due_date\": <ISO datetime>}\n"
                    "If the intent is unclear, return: {\"action\": \"say\", \"message\": <text>}"
                ),
            },
            {"role": "user", "content": text},
        ]
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )
        response_content = completion.choices[0].message.content.strip()
        intent = json.loads(response_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent resolution failed: {e}")

    tts_text = ""
    if intent.get("action") == "update_device":
        from smart_home.routers.home_control import devices_db
        device_id = intent.get("device_id")
        status = intent.get("status")
        for device in devices_db:
            if device.id == device_id:
                device.status = status
                device.last_updated = datetime.now()
                tts_text = f"Set {device.name} to {status}"
                break
        else:
            tts_text = "Device not found"
    elif intent.get("action") == "create_reminder":
        import life_organizer.routers.reminders as reminders_module
        Reminder = reminders_module.Reminder
        try:
            due_date = datetime.fromisoformat(intent.get("due_date"))
        except Exception:
            due_date = datetime.now()
        new_reminder = Reminder(
            id=reminders_module.reminder_id_counter,
            title=intent.get("title", "Reminder"),
            description=None,
            due_date=due_date,
            priority=1,
            created_at=datetime.now(),
            completed=False,
        )
        reminders_module.reminders_db.append(new_reminder)
        reminders_module.reminder_id_counter += 1  # type: ignore
        tts_text = f"Added reminder {new_reminder.title}"
    else:
        tts_text = intent.get("message", text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_out:
        tts = gTTS(tts_text)
        tts.save(tmp_out.name)
        audio_out = tmp_out.name

    return FileResponse(audio_out, media_type="audio/mpeg", filename="response.mp3")
