from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.markups import training_markup


async def training_handler(message: Message, bot: AsyncTeleBot):
    word_id = 5  # fixme: get_next_word(message.from_user.id)
    await bot.send_message(
        message.chat.id,
        "Начинаем тренировку!",
        reply_markup=training_markup(word_id),
    )
