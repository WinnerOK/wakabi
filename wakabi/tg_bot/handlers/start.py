from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.markups import language_level_markup


async def start_handler(message: Message, bot: AsyncTeleBot):
    await bot.send_message(
        message.chat.id,
        dedent(
            f"""
            Привет, {message.from_user.full_name}!
            Прежде, чем мы начнем, скажи какой у тебя уровень владения языком
            """,
        ),
        reply_markup=language_level_markup(),
    )
