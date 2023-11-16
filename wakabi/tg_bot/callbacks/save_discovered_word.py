import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from wakabi.repository.user import add_word_to_learn
from wakabi.tg_bot.callbacks.types import word_discovery_data


async def save_discovered_word_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = word_discovery_data.parse(callback_data=call.data)

    async with pool.acquire() as conn:
        await add_word_to_learn(conn, call.from_user.id, callback_data["word"])

    await bot.edit_message_text(
        call.message.html_text + "\n\nAdded new word to your vocabulary",
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
