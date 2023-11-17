import typing

import asyncio

import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi import definition
from wakabi.tg_bot.markups import add_to_vocabulary_markup


async def definition_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    tasks = set()
    word: str = message.text.strip().lower()
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        async with conn.transaction():
            try:
                word_data: list[definition.WordData] = await definition.get_word_data(
                    word,
                    conn,
                )
            except definition.NetworkException:
                bot_msg = definition.get_network_exception_msg()
                await bot.reply_to(
                    message,
                    text=bot_msg,
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=True,
                )
                return
            if word_data:
                word_info_formatted: str = definition.get_word_info_formatted(
                    word=word,
                    word_data=word_data,
                )
                bot_msg = word_info_formatted
                if not await definition.is_word_exists_in_db(word, conn):
                    for data in word_data:
                        task = asyncio.create_task(
                            definition.add_new_word_into_db(
                                word=word,
                                definition=data.definition,
                                phonetics=data.phonetics,
                                pos=data.pos,
                                conn=conn,
                            ),
                        )
                        tasks.add(task)
                        task.add_done_callback(tasks.discard)
            else:
                bot_msg = await definition.get_not_found_word_msg(word)

            word_voices_url: list[str] = definition.get_word_voice_url(
                word_data,
            )
            if len(set(word_voices_url)) == 1:
                await bot.send_voice(
                    chat_id=message.chat.id,
                    voice=word_voices_url[0],
                    parse_mode="MarkdownV2",
                )

            await bot.reply_to(
                message,
                text=bot_msg,
                parse_mode="MarkdownV2",
                disable_web_page_preview=True,
                reply_markup=add_to_vocabulary_markup(word) if word_data else None,
            )
