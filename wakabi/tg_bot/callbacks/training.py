from textwrap import dedent

import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

import wakabi.repository.training as training_repo

from wakabi import definition
from wakabi.tg_bot.callbacks.types import (
    TrainingExerciseStatus,
    exit_training_data,
    training_iteration_end_data,
    training_iteration_start_data,
)
from wakabi.tg_bot.markups import (
    training_iteration_end_markup,
)
from wakabi.tg_bot.utils.training import build_statistics_str, start_training_iteration


async def training_iteration_start_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = training_iteration_start_data.parse(callback_data=call.data)

    await start_training_iteration(
        message=call.message,
        bot=bot,
        pool=pool,
        send_new_message=False,
        correct_answers_counter=int(callback_data["correct_count"]),
        incorrect_answers_counter=int(callback_data["incorrect_count"]),
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
            word_id,
        )

    word = pg_result[0]["word"]

    word_info: str = definition.get_word_info_formatted(
        word=word,
        word_data=(
            await definition.get_word_data(
                word,
                pool
            )
        ),
    )

    if callback_data['status'] == 'fail':
        text = word_info
    else:
        text = "*Go next\? Press the button\!*"
    await bot.edit_message_text(
        text=dedent(
            f"{word}\n\n"
            f"{text}"
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=training_iteration_end_markup(
            correct_count=correct_count,
            incorrect_count=incorrect_count,
        ),
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )


async def exit_training_callback(call: CallbackQuery, bot: AsyncTeleBot) -> None:
    callback_data: dict = exit_training_data.parse(callback_data=call.data)
    correct_count = int(callback_data["correct_count"])
    incorrect_count = int(callback_data["incorrect_count"])

    text: str
    if correct_count + incorrect_count == 0:
        text = "That's all folks!"
    else:
        text = dedent(
            f"""
                {
                    build_statistics_str(
                        correct_answers_counter=int(callback_data["correct_count"]),
                        incorrect_answers_counter=int(callback_data["incorrect_count"]),
                    )
                }
            """,
        )

    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
    )
