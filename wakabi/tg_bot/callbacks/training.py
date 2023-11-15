import asyncpg

from textwrap import dedent
from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from wakabi.tg_bot.callbacks.types import (
    training_iteration_start_data,
    training_iteration_end_data,
)
from wakabi.tg_bot.markups import (
    training_iteration_start_markup,
    training_iteration_end_markup,
)

import wakabi.repository.training as training_repo


async def training_iteration_start_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = training_iteration_start_data.parse(callback_data=call.data)
    word_id = int(callback_data["word_id"]) + 1  # TODO: pass to PG request
    # SELECT new word

    pg_result: list[asyncpg.Record]
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        pg_result = await training_repo.get_word_by_user(conn, call.from_user.id)

    if not pg_result:
        print("IN if not pg_result")
        pass  # TODO: !!!

    word, word_id = (
        pg_result[0]["word"],
        pg_result[0]["word_id"],
    )  # here word_id is id of the new word

    await bot.edit_message_text(
        text=word,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=training_iteration_start_markup(  # TODO: pass statistics from request
            word_id=word_id,
            correct_count=2,  # hardcoded
            incorrect_count=3,  # hardcoded
        ),
    )


async def training_iteration_end_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = training_iteration_end_data.parse(callback_data=call.data)
    word_id = int(callback_data["word_id"]) + 1
    # status = bool(callback_data["status"]) # TODO: pass status
    status = False  # TODO: pass status

    async with pool.acquire() as conn:  # type: asyncpg.Connection
        await training_repo.update_word_after_train(
            conn,
            call.from_user.id,
            word_id,
            status,
        )

    pg_result: list[asyncpg.Record]
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        pg_result = await training_repo.get_definition_by_word_id(
            conn,
            call.from_user.id,
            word_id,
            status,
        )

    if not pg_result:
        print("IN if not result")
        pass  # TODO: !!!

    word, definition = pg_result[0]["word"], pg_result[0]["definition"]

    await bot.edit_message_text(
        text=dedent(
            f"""
                {word}
                {definition}
            """
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=training_iteration_end_markup(  # TODO: pass statistics from request
            previous_word_id=word_id,
            correct_count=2,  # hardcoded
            incorrect_count=3,  # hardcoded
        ),
    )


async def exit_training_callback(query: CallbackQuery, bot: AsyncTeleBot) -> None:
    print("in exit_training_callback")  # TODO: implement me
    pass
