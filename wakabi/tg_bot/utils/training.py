from typing import Optional

from textwrap import dedent

import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.repository.training import get_word_by_user
from wakabi.tg_bot.markups import training_iteration_start_markup


def build_statistics_str(
    correct_answers_counter: int = 0,
    incorrect_answers_counter: int = 0,
) -> Optional[str]:
    total = correct_answers_counter + incorrect_answers_counter
    if not total:
        return None
    ratio = (
        correct_answers_counter / incorrect_answers_counter
        if incorrect_answers_counter
        else 1.0
    )
    return dedent(
        f"""
            Training is finished! Statistics are below:

            Total answers: {total}
            Correct answers: {correct_answers_counter}
            Incorrect answers: {incorrect_answers_counter}
            Accuracy: {ratio:.0%}
        """,
    )


async def start_training_iteration(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
    send_new_message: bool = True,
    # previous_word_id: Optional[int] = None,
    correct_answers_counter: int = 0,
    incorrect_answers_counter: int = 0,
) -> None:
    pg_result: list[asyncpg.Record]
    async with pool.acquire() as conn:
        pg_result = await get_word_by_user(conn, message.from_user.id)

    # function = bot.send_message if send_new_message else bot.edit_message_text
    if not pg_result:  # code duplication
        if send_new_message:
            await bot.send_message(
                text="All words are learned. You are breathtaking!",
                chat_id=message.chat.id,
            )
        else:
            await bot.edit_message_text(
                text=dedent(
                    f"""
                        All words are learned. You are breathtaking!
                        {
                            build_statistics_str(
                                correct_answers_counter=correct_answers_counter,
                                incorrect_answers_counter=incorrect_answers_counter,
                            )
                        }
                    """,
                ),
                chat_id=message.chat.id,
                message_id=message.id,
            )
    else:
        new_word, new_word_id = (
            pg_result[0]["word"],
            pg_result[0]["word_id"],
        )
        if send_new_message:
            await bot.send_message(
                text=new_word,
                chat_id=message.chat.id,
                reply_markup=training_iteration_start_markup(
                    word_id=new_word_id,
                ),
            )
        else:
            await bot.edit_message_text(
                text=new_word,
                chat_id=message.chat.id,
                message_id=message.id,
                reply_markup=training_iteration_start_markup(
                    word_id=new_word_id,
                    correct_count=correct_answers_counter,
                    incorrect_count=incorrect_answers_counter,
                ),
            )
