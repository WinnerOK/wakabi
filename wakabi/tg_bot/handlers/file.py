from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.markups import language_level_markup

import wakabi.tg_bot.process as process


import aiohttp


async def read_file(file_id: str, bot: AsyncTeleBot):
    file_url = await bot.get_file_url(file_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            file_content = await response.text()
    return file_content

allowed_extensions = [".txt"]       
learning_words = ["hello", "world"] # words that user already have in his learning vocabulary
level_words = ["how", "are", "you"] # words that we suppose user knows


async def file_handler(message: Message, bot: AsyncTeleBot):
    if not message.document:
        return

    if not any(message.document.file_name.lower().endswith(ext) for ext in allowed_extensions):
        await bot.reply_to(message, "Sorry, this file type is not supported yet.")
        return

    await bot.reply_to(message, "Processing...")

    file_id = message.document.file_id
    file_content = await read_file(file_id, bot)
    words_to_learn = process.process_text(file_content, learning_words, level_words, words_limit=10)
    if len(words_to_learn) == 0:
        await bot.reply_to(message, "Sorry, I can't find any words to learn.")
        return
    
    await bot.reply_to(message, str(words_to_learn))
