import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.markups import training_iteration_start_markup

import wakabi.repository.training as training_repo


async def training_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    user_id = message.from_user.id

    pg_result: list[asyncpg.Record]
    async with pool.acquire() as conn:
        pg_result = await training_repo.get_word_by_user(conn, user_id)

    new_word: str
    new_word_id: int
    if not pg_result:
        print("IN if not pg_result")
        new_word = "dummy_word"
        new_word_id = "0"
        pass  # TODO(mr-nikulin): handle bad pg_result
    else:
        new_word, new_word_id = (
            pg_result[0]["word"],
            pg_result[0]["word_id"],
        )

    await bot.send_message(
        text=new_word,
        chat_id=message.chat.id,
        reply_markup=training_iteration_start_markup(
            new_word_id,
        ),
    )
