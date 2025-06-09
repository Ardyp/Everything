import pyttsx3

engine = pyttsx3.init()

def speak(text: str) -> None:
    """Speak text using pyttsx3."""
    engine.say(text)
    engine.runAndWait()
