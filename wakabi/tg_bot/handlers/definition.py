import typing

import aiohttp
import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

HTTPS_PROTOCOL_STATIC = 'https://'
DICTIONARY_API_URL = 'api.dictionaryapi.dev/api/v2/entries/en/{word}'
GPT_CHAT_WEB_URL = 'you.com/search?q={word}'
YANDEX_IMAGES_WEB_URL = 'yandex.ru/images/search?text={word}'
YOUGLISH_ENGLISH_WEB_URL = 'youglish.com/pronounce/{word}/english'

NO_DEFINITIONS_FOUND_API_MSG = 'No Definitions Found'


def _get_word_definition_formatted(
    word: str,
    word_definition_raw: str,
) -> str:
    yandex_content_by_word: str = (
        HTTPS_PROTOCOL_STATIC + YANDEX_IMAGES_WEB_URL.format(
            word=word,
        )
    )
    youglish_content_by_word: str = (
        HTTPS_PROTOCOL_STATIC + YOUGLISH_ENGLISH_WEB_URL.format(
            word=word,
        )
    )
    word_definition_formatted: str = (
        f"**Определение** слова **{word}**:\n  {word_definition_raw}\n"
        f"Полезное **медиа**: \n"
        f"[Look at images by word **{word}**!]({yandex_content_by_word}) \n"
        f"[Train your pronunciation for word **{word}**!]"
        f"({youglish_content_by_word})\n"
    )
    return word_definition_formatted


async def _get_word_definition_from_dictionary_api(
    word: str
) -> typing.Optional[str]:
    definitions: typing.List[str] = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            HTTPS_PROTOCOL_STATIC + DICTIONARY_API_URL.format(word=word)
        ) as response:
            data = await response.json()
            if (
                isinstance(data, dict)
                and
                data.get('title') == NO_DEFINITIONS_FOUND_API_MSG
            ):
                return None
            for definition in data[0]["meanings"]["definitions"]:
                definitions.append(definition + '\n')
            return ''.join(definitions)


async def _is_word_exists_in_db(
    word: str,
) -> typing.Optional[str]:
    conn = await asyncpg.connect(
        user='user', password='password',
        database='database', host='host'
    )
    result = await conn.fetch(
        'SELECT word FROM words WHERE word = $1',
        word
    )
    await conn.close()
    return result


async def _get_word_definition_from_db(
    word: str,
) -> typing.Optional[str]:
    conn = await asyncpg.connect(
        user='user', password='password',
        database='database', host='host'
    )
    result = await conn.fetch(
        'SELECT definition FROM words WHERE word = $1',
        word
    )
    await conn.close()
    return result


async def get_not_found_word_msg(
    word: str,
) -> str:
    return (
        f"Sorry bro, I don't know word: **{word}**! :("
        f"Try find something information in [**chatGPT**]("
        f"{HTTPS_PROTOCOL_STATIC + GPT_CHAT_WEB_URL.format(word)}"
        f")"
    )

async def add_new_word_into_db(
    word: str,
    definition: str,
) -> None:
    conn = await asyncpg.connect(
        user='user', password='password',
        database='database', host='host'
    )
    await conn.execute(
        'INSERT INTO words(word, definition, level) VALUES ($1, $2, $3)',
        word,
        definition,
        'B1'
    )


async def get_word_definition(
    word: str,
) -> typing.Optional[str]:
    word_definition_from_db: typing.Optional[str] = (
        await _get_word_definition_from_db(word)
    )
    if word_definition_from_db:
        return word_definition_from_db
    word_definition_from_dictionary_api: typing.Optional[
        str
    ] = await _get_word_definition_from_dictionary_api(
        word
    )
    return word_definition_from_dictionary_api


async def definition_handler(message: Message, bot: AsyncTeleBot):
    word: str = message.text.strip().lower()
    bot_msg: str
    if word:
        word_definition_raw: str = await get_word_definition(word)
        if word_definition_raw:
            word_definition_formatted: str = _get_word_definition_formatted(
                word=word,
                word_definition_raw=word_definition_raw,
            )
            bot_msg = word_definition_formatted
        else:
            bot_msg = await get_not_found_word_msg(word)
        await bot.send_message(
            chat_id=message.chat.id,
            text=bot_msg,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
        if not await _is_word_exists_in_db(word):
            await add_new_word_into_db(
                word=word,
                definition=word_definition_raw,
            )
