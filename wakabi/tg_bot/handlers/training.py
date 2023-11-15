from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.markups import training_iteration_start_markup


async def training_handler(message: Message, bot: AsyncTeleBot):
    word = "dog"
    word_id = 1  # TODO: get_next_word(message.from_user.id) - SELECT

    await bot.send_message(
        text=word,
        chat_id=message.chat.id,
        reply_markup=training_iteration_start_markup(
            word_id,
        ),
    )
