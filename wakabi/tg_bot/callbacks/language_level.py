import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

import wakabi.repository.user as user_repo

from wakabi.tg_bot.callbacks.types import language_level_data


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
    await bot.send_message(
        call.from_user.id,
        f"Запомнил, твой уровень {callback_data['level'].upper()}",
    )
