from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from .routers.appointments import appointments_db
from .routers.reminders import reminders_db
from .routers.notifications import notify_all

scheduler = BackgroundScheduler()


def check_upcoming() -> None:
    now = datetime.utcnow()
    threshold = now + timedelta(minutes=10)
    for appt in appointments_db:
        if now <= appt.start_time <= threshold:
            notify_all("Upcoming appointment", f"{appt.title} at {appt.start_time.isoformat()}")
    for rem in reminders_db:
        if not rem.completed and now <= rem.due_date <= threshold:
            notify_all("Reminder due", f"{rem.title} at {rem.due_date.isoformat()}")


def start() -> None:
    if not scheduler.running:
        scheduler.add_job(check_upcoming, "interval", minutes=1)
        scheduler.start()
