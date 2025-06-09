from fastapi import APIRouter, HTTPException, Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import os
import json
from .appointments import Appointment, appointments_db, appointment_id_counter

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")
REDIRECT_URI = os.getenv("GOOGLE_CALENDAR_REDIRECT_URI", "http://localhost:8000/calendar/callback")

router = APIRouter(prefix="/calendar", tags=["calendar"])
_state = {}

@router.get("/auth")
async def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    _state["state"] = state
    return {"auth_url": auth_url}

@router.get("/callback")
async def oauth_callback(request: Request):
    state = _state.get("state")
    if not state:
        raise HTTPException(status_code=400, detail="OAuth state missing")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials
    with open("google_credentials.json", "w") as f:
        f.write(creds.to_json())
    return {"status": "authorized"}

@router.post("/sync")
async def sync_calendar():
    if not os.path.exists("google_credentials.json"):
        raise HTTPException(status_code=400, detail="Google account not linked")
    creds = Credentials.from_authorized_user_file("google_credentials.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)
    now = datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(calendarId="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime").execute()
    events = events_result.get("items", [])
    global appointment_id_counter
    added = 0
    for event in events:
        start = event.get("start", {}).get("dateTime")
        end = event.get("end", {}).get("dateTime")
        if not start or not end:
            continue
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        if any(a.start_time == start_dt and a.title == event.get("summary") for a in appointments_db):
            continue
        appt = Appointment(
            id=appointment_id_counter,
            title=event.get("summary", "Event"),
            description=event.get("description"),
            start_time=start_dt,
            end_time=end_dt,
            location=event.get("location"),
            created_at=datetime.utcnow(),
        )
        appointments_db.append(appt)
        appointment_id_counter += 1
        added += 1
    return {"events_added": added}
