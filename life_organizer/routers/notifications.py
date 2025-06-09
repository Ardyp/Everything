from fastapi import APIRouter
from typing import Dict, Any
import json
import os
import requests
from pywebpush import webpush, WebPushException

router = APIRouter(prefix="/notifications", tags=["notifications"])

expo_tokens = set()
webpush_subscriptions = []

@router.post("/register/expo")
async def register_expo(token: str):
    expo_tokens.add(token)
    return {"message": "Expo token registered"}

@router.post("/register/web")
async def register_web(subscription: Dict[str, Any]):
    webpush_subscriptions.append(subscription)
    return {"message": "Web push subscription registered"}


def _send_expo(token: str, title: str, body: str) -> None:
    message = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": body,
    }
    try:
        requests.post("https://exp.host/--/api/v2/push/send", json=message, timeout=5)
    except Exception as e:
        print(f"Expo push failed: {e}")


def _send_web(subscription: Dict[str, Any], data: Dict[str, Any]) -> None:
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(data),
            vapid_private_key=os.getenv("VAPID_PRIVATE_KEY", ""),
            vapid_claims={"sub": "mailto:example@example.com"},
        )
    except WebPushException as ex:
        print(f"Web push failed: {ex}")


def notify_all(title: str, body: str) -> None:
    for token in list(expo_tokens):
        _send_expo(token, title, body)
    for sub in list(webpush_subscriptions):
        _send_web(sub, {"title": title, "body": body})
