from telebot.async_telebot import AsyncTeleBot
from telebot.callback_data import CallbackData
from telebot.types import CallbackQuery

language_level = CallbackData("level", prefix="lang_level")


async def language_level_callback(call: CallbackQuery, bot: AsyncTeleBot) -> None:
    callback_data: dict = language_level.parse(callback_data=call.data)
    await bot.send_message(
        call.from_user.id,
        f"Запомнил, твой уровень {callback_data['level']}",
    )
