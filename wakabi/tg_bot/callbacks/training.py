import asyncpg

from textwrap import dedent
from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from wakabi.tg_bot.callbacks.types import (
    TrainingExerciseStatus,
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
    previous_word_id = int(
        callback_data["word_id"]
    )  # TODO(mr-nikulin): pass to PG request
    correct_count = int(callback_data["correct_count"])
    incorrect_count = int(callback_data["incorrect_count"])

    pg_result: list[asyncpg.Record]
    async with pool.acquire() as conn:
        pg_result = await training_repo.get_word_by_user(conn, call.from_user.id)

    new_word: str
    new_word_id: int
    if not pg_result:
        # слова закончились
        print("IN if not pg_result")
        new_word = "dummy_word"
        new_word_id = "0"
        pass  # TODO(mr-nikulin): handle bad pg_result
    else:
        new_word, new_word_id = (
            pg_result[0]["word"],
            pg_result[0]["word_id"],
        )

    await bot.edit_message_text(
        text=new_word,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=training_iteration_start_markup(
            word_id=new_word_id,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
        ),
    )


async def training_iteration_end_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = training_iteration_end_data.parse(callback_data=call.data)
    word_id = int(callback_data["word_id"])
    correct_count = int(callback_data["correct_count"])
    incorrect_count = int(callback_data["incorrect_count"])
    print(f'callback_data["status"]={callback_data["status"]}')
    status = (
        TrainingExerciseStatus(callback_data["status"]) == TrainingExerciseStatus.passed
    )

    async with pool.acquire() as conn:
        await training_repo.update_word_after_training_iteration(
            conn,
            call.from_user.id,
            word_id,
            status,
        )

    pg_result: list[asyncpg.Record]
    async with pool.acquire() as conn:
        pg_result = await training_repo.get_definition_by_word_id(
            conn,
            call.from_user.id,
        )

    word: str
    definition: str

    if not pg_result:
        print("IN if not pg_result")
        word = "dummy_word"
        definition = "dummy_definition"
        pass  # TODO(mr-nikulin): handle bad pg_result
    else:
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
        reply_markup=training_iteration_end_markup(
            previous_word_id=word_id,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
        ),
    )


async def exit_training_callback(call: CallbackQuery, bot: AsyncTeleBot) -> None:
    await bot.send_message(
        text="Конец, а кто учил слова - тот молодец (тут будет статистика по тренировке)",
        chat_id=call.message.chat.id,
    )
    print("in exit_training_callback")  # TODO: implement me
    pass
