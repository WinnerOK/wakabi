from wakabi.tg_bot.handlers.definition import definition_handler
from wakabi.tg_bot.handlers.file import file_handler
from wakabi.tg_bot.handlers.help import BOT_COMMANDS, get_help_message, help_handler
from wakabi.tg_bot.handlers.start import start_handler
from wakabi.tg_bot.handlers.training import training_handler

__all__ = [
    "start_handler",
    "training_handler",
    "definition_handler",
    "help_handler",
    "get_help_message",
    "BOT_COMMANDS",
    "file_handler",
]
