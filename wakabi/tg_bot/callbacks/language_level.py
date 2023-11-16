import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

import wakabi.repository.user as user_repo

from wakabi.tg_bot.callbacks.types import language_level_data
from wakabi.tg_bot.handlers import get_help_message


async def language_level_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = language_level_data.parse(callback_data=call.data)
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        await user_repo.upsert_user_level(
            conn,
            call.from_user.id,
            callback_data["level"],
        )
    await bot.edit_message_text(
        f"Your English level is {callback_data['level'].upper()}",
        message_id=call.message.id,
        chat_id=call.message.chat.id,
    )
    await bot.send_message(call.message.chat.id, get_help_message())
