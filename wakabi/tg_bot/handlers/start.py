from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


async def start_handler(message: Message, bot: AsyncTeleBot):
    await bot.send_message(message.chat.id, f"Hello, {message.from_user.full_name}!")
