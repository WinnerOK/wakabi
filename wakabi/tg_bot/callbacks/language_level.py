from telebot.async_telebot import AsyncTeleBot
from telebot.callback_data import CallbackData
from telebot.types import CallbackQuery

from wakabi.tg_bot.callbacks.types import language_level_data


async def language_level_callback(call: CallbackQuery, bot: AsyncTeleBot) -> None:
    callback_data: dict = language_level_data.parse(callback_data=call.data)
    await bot.send_message(
        call.from_user.id,
        f"Запомнил, твой уровень {callback_data['level']}",
    )
