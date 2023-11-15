from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.markups import training_markup


def parse_training_iterations_from_request(message: Message) -> int:
    DEFAULT_TRAINING_ITERATIONS = 5
    training_iterations = DEFAULT_TRAINING_ITERATIONS
    splitted_message = message.text.split(" ")
    if len(splitted_message) > 1:
        training_iterations = int(splitted_message[1])
    return training_iterations


async def training_handler(message: Message, bot: AsyncTeleBot):
    word_id = 5  # fixme: get_next_word(message.from_user.id)

    training_iterations = parse_training_iterations_from_request(message)
    await bot.send_message(
        message.chat.id,
        "Начинаем тренировку!",
        reply_markup=training_markup(word_id),
    )
