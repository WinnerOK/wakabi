from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, Message

BOT_COMMANDS = [
    BotCommand("/start", "Change your language proficiency level"),
    BotCommand("/help", "Show this help message"),
    BotCommand("/training", "Start a training"),
]


def get_help_message() -> str:
    return (
        "Available commangs:\n"
        + "\n".join([f"{cmd.command} - {cmd.description}" for cmd in BOT_COMMANDS])
        + "\nYou can also ask me about an unfamiliar word "
          "or send me the subtitles of your favorite TV series (in .srt format) "
          "so that I can show you unfamiliar words."
    )


async def help_handler(message: Message, bot: AsyncTeleBot):
    await bot.send_message(
        message.chat.id,
        get_help_message(),
    )
