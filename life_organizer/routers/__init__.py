from .reminders import router as reminders
from .appointments import router as appointments
from .location import router as location

__all__ = ["reminders", "appointments", "location"]
