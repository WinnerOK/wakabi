from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from wakabi.tg_bot.callbacks.types import word_discovery_data


async def save_discovered_word_callback(call: CallbackQuery, bot: AsyncTeleBot) -> None:
    callback_data: dict = word_discovery_data.parse(callback_data=call.data)
    _ = callback_data
    # todo add newly discovered word to user's learn list

    await bot.edit_message_text(
        call.message.html_text + "\n\nAdded new word to your vocabulary",
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        parse_mode="HTML",
    )
