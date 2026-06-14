from . import Virel
from .functions.login import apply_login_patch

import asyncio
import logging
import time

from logging import Formatter, StreamHandler
from contextlib import suppress

class CustomFormatter(Formatter):
    """
    Custom logging formatter to add colors and formatting to log messages.
    """
    def __init__(self):
        self.colors = {
            "DEBUG": "\033[36m",
            "INFO": "\033[36m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
            "CRITICAL": "\033[35m",
        }
        self.reset = "\033[0m"

    def format(self, record):
        """
        Format the log record with colors and timestamps.
        """
        shorttime = time.strftime("%H:%M:%S", time.localtime(record.created))
        fulltime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        color = self.colors.get(record.levelname, "")
        levelname = f"{color}{record.levelname}{self.reset}"
        fulltime_colored = f"\033[95m{fulltime}{self.reset}"
        shorttime_colored = f"\033[95m{shorttime}{self.reset}"
        name_colored = f"\033[34m{record.name}{self.reset}"
        message_colored = f"\033[90m{record.getMessage()}{self.reset}"
        return f"{levelname} — {fulltime_colored} ({shorttime_colored}) [{name_colored}]: {message_colored}"

handler = StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

with suppress(KeyboardInterrupt):
    apply_login_patch()
    bot = Virel()
    asyncio.run(bot.run())
