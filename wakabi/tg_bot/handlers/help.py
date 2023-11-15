from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, Message

BOT_COMMANDS = [
    BotCommand("/start", "Сменить свой уровень владения языком"),
    BotCommand("/help", "Вывести сообщение с доступными командами"),
    BotCommand("/training", "Начать тренировку"),
]


def get_help_message() -> str:
    return (
        "Доступные команды:\n"
        + "\n".join([f"{cmd.command} - {cmd.description}" for cmd in BOT_COMMANDS])
        + "\nА еще ты можешь просто спросить меня о незнакомом слове "
        "или прислать мне субтитры твоего любимого сериала"
    )


async def help_handler(message: Message, bot: AsyncTeleBot):
    await bot.send_message(
        message.chat.id,
        get_help_message(),
    )
