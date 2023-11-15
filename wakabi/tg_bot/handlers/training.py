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
    # word = "dog"
    # word_id = 1
    # select

    pg_result: list[asyncpg.Record]
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        pg_result = await training_repo.get_word_by_user(conn, user_id)

    if not pg_result:
        print("IN if not pg_result")
        pass  # TODO: !!!

    word, word_id = (
        pg_result[0]["word"],
        pg_result[0]["word_id"],
    )  # here word_id is id of the new word

    await bot.send_message(
        text=word,
        chat_id=message.chat.id,
        reply_markup=training_iteration_start_markup(
            word_id,
        ),
    )
