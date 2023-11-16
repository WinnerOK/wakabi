import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.utils.training import start_training_iteration


async def training_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    await start_training_iteration(
        message=message,
        bot=bot,
        pool=pool,
    )
