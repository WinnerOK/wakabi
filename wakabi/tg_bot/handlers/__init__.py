from wakabi.tg_bot.handlers.discovery import discovery_handler
from wakabi.tg_bot.handlers.help import BOT_COMMANDS, get_help_message, help_handler
from wakabi.tg_bot.handlers.start import start_handler
from wakabi.tg_bot.handlers.training import training_handler

__all__ = [
    "start_handler",
    "training_handler",
    "discovery_handler",
    "help_handler",
    "get_help_message",
    "BOT_COMMANDS",
]
