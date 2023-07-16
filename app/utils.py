from datetime import datetime
from core.config import Config


def get_current_time():
    return datetime.now(Config.TIMEZONE).replace(tzinfo=None)