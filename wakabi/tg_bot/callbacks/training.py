from enum import Enum
from textwrap import dedent

import telebot.formatting as fmt

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from wakabi.tg_bot.callbacks.types import TrainingExerciseStatus, training_data
from wakabi.tg_bot.markups import training_markup


async def training_callback(call: CallbackQuery, bot: AsyncTeleBot) -> None:
    callback_data: dict = training_data.parse(callback_data=call.data)
    word_id = int(callback_data["word_id"]) + 1
    await bot.edit_message_text(
        fmt.format_text(
            fmt.escape_markdown(
                dedent(
                    f"""
                    {callback_data['status']=}
                    {word_id=}
                    """,
                ),
            ),
            fmt.mspoiler("Here is the definition"),
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=training_markup(
            word_id,
            int(callback_data["correct_count"]),
            int(callback_data["incorrect_count"]),
        ),
        parse_mode="MarkdownV2",
    )
