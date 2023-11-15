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


async def training_iteration_start_callback(
    call: CallbackQuery, bot: AsyncTeleBot
) -> None:
    callback_data: dict = training_iteration_start_data.parse(callback_data=call.data)
    word_id = int(callback_data["word_id"]) + 1
    # SELECT new word

    word = "some_word_from_callback"
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
    call: CallbackQuery, bot: AsyncTeleBot
) -> None:
    callback_data: dict = training_iteration_end_data.parse(callback_data=call.data)
    word_id = int(callback_data["word_id"]) + 1
    # TODO: UPDATE DB.
    # TODO: select definition + word(str) by word_id
    # edit message: word + definition
    # 2 buttons: "Continue", "Exit"

    word = "some_word_from_callback"
    definition = "definition"
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
    print("in exit_training_callback")
    pass
