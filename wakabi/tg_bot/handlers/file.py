from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

import wakabi.tg_bot.process as process


from textwrap import dedent

import aiohttp
import asyncpg


allowed_extensions = [".txt",  ".srt"]
# TODO: get words from DB
learning_words = ["hello", "world"]
level_words = ["how", "are", "you"]


import pysrt
async def read_file(file_id: str, bot: AsyncTeleBot):
    file_url = await bot.get_file_url(file_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            file_content = await response.text()
    file_ext = file_url.split('.')[-1]
    if file_ext == 'srt':
        subs = pysrt.from_string(file_content)
        file_content = "\n".join(sub.text for sub in subs)
    return file_content


async def file_handler(message: Message, bot: AsyncTeleBot):
    if not message.document:
        return
    
    file_name = message.document.file_name.lower()
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        await bot.reply_to(message, "Sorry, this file type is not supported yet.")
        return

    await bot.reply_to(message, "Processing...")

    file_id = message.document.file_id
    
    file_content = await read_file(file_id, bot)

    words_to_learn = process.process_text(file_content, learning_words, level_words, words_limit=30)

    if len(words_to_learn) == 0:
        await bot.reply_to(message, "Sorry, I can't find any words to learn.")
        return

    reply  = "Here's most popular words to learn from text: " + ", ".join(words_to_learn) + '.'
    await bot.reply_to(message, reply)

    # TODO: add words to db
    # reply = "Do you want to add these words to your vocabulary?"

    # await bot.send_message(
    #     text=reply,
    #     chat_id=message.chat.id,
    #     reply_markup=add_parsed_words_markup(
    #         words_to_learn
    #     ),
    # )

