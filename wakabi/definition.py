import typing

import dataclasses
import enum
import re

import aiohttp
import asyncpg

from telebot import formatting

HTTPS_PROTOCOL_STATIC = "https://"
DICTIONARY_API_URL = "api.dictionaryapi.dev/api/v2/entries/en/{word}"
GPT_CHAT_WEB_URL = (
    "you.com/search?q=Please, "
    "give me definitions for word: '{word}'\n"
    "If you can, make it in form like this: pos, phonetics, definition"
    "&tbm=youchat"
)
YANDEX_IMAGES_WEB_URL = "yandex.ru/images/search?text={word}"
YOUGLISH_ENGLISH_WEB_URL = "youglish.com/pronounce/{word}/english"

NO_DEFINITIONS_FOUND_API_MSG = "No Definitions Found"

MAX_COUNT_DEFINITIONS = 3

BRACKETS_SANITIZER_PATTERN = r"\(.*?\)|\."
SPACE_SANITIZER_PATTERN = r"^\s+|\s+$"
SPECIALIZED_SYMBOLS_PATTERN = r"([.?!\-])"


@dataclasses.dataclass
class WordData:
    word: str
    definition: typing.Optional[str] = None
    pos: typing.Optional[str] = None
    phonetics: typing.Optional[str] = None
    voice_url: typing.Optional[str] = None


class NetworkException(Exception):
    pass


class DefinitionFields(enum.Enum):
    AUDIO = "audio"
    DEFINITION = "definition"
    DEFINITIONS = "definitions"
    MEANINGS = "meanings"
    PART_OF_SPEACH = "partOfSpeech"
    PHONETIC = "phonetic"


def _format_string(
    string_raw: typing.Optional[str],
) -> str:
    if not string_raw:
        return ""
    string_without_brackets: str = (
        re.sub(
            BRACKETS_SANITIZER_PATTERN,
            "",
            string_raw,
        )
        if re.search(BRACKETS_SANITIZER_PATTERN, string_raw)
        else string_raw
    )
    string_without_useless_space: str = (
        re.sub(
            SPACE_SANITIZER_PATTERN,
            "",
            string_without_brackets,
        )
        if re.search(SPACE_SANITIZER_PATTERN, string_without_brackets)
        else string_without_brackets
    )
    string_prepared: str = (
        re.sub(
            SPECIALIZED_SYMBOLS_PATTERN,
            "",
            string_without_useless_space,
        )
        if re.search(SPECIALIZED_SYMBOLS_PATTERN, string_without_useless_space)
        else string_without_useless_space
    )
    return string_prepared


def _get_word_data_as_definitions(
    word_data: list[WordData],
) -> str:
    definitions: list[str] = []
    for data in word_data:
        definition_prepared = ""
        if data.pos:
            definition_prepared += "*" + _format_string(data.pos) + "*" + "; "
        if data.phonetics:
            definition_prepared += (
                _format_string(
                    formatting.escape_markdown(data.phonetics),
                )
                + "; "
            )
        definition_prepared += (
            _format_string(
                formatting.escape_markdown(data.definition),
            )
            + "\n"
        )
        definitions.append(
            definition_prepared,
        )
    return "".join(definitions)


def get_word_info_formatted(
    word: str,
    word_data: list[WordData],
) -> str:
    yandex_content_by_word: str = HTTPS_PROTOCOL_STATIC + YANDEX_IMAGES_WEB_URL.format(
        word=word,
    )
    youglish_content_by_word: str = (
        HTTPS_PROTOCOL_STATIC
        + YOUGLISH_ENGLISH_WEB_URL.format(
            word=word,
        )
    )
    word_data_definitions = _format_string(
        _get_word_data_as_definitions(word_data),
    )
    word_info_formatted: str = (
        f"*Definitions* of word *{word}*:\n{word_data_definitions}\n\n"
        f"Useful *media* resources: \n"
        f"[Look at images by word *{word}*\\!]({yandex_content_by_word}) \n"
        rf"[Train your pronunciation for word *{word}*\!]"
        f"({youglish_content_by_word})\n"
    )
    return word_info_formatted


async def _get_word_data_from_dictionary_api(
    word: str,
) -> list[WordData]:
    results: list[WordData] = []
    count_definitions: int = 0
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                HTTPS_PROTOCOL_STATIC + DICTIONARY_API_URL.format(word=word),
            ) as response:
                data = await response.json()
                if (
                    isinstance(data, dict)
                    and data.get("title") == NO_DEFINITIONS_FOUND_API_MSG
                ):
                    return results
                for definition in data[0][DefinitionFields.MEANINGS.value]:
                    if count_definitions > MAX_COUNT_DEFINITIONS:
                        break
                    results.append(
                        WordData(
                            word=word,
                            definition=definition[DefinitionFields.DEFINITIONS.value][
                                0
                            ][DefinitionFields.DEFINITION.value],
                            phonetics=data[0][DefinitionFields.PHONETIC.value],
                            pos=definition[DefinitionFields.PART_OF_SPEACH.value],
                        ),
                    )
                    count_definitions += 1
                return results
        except Exception:
            raise NetworkException


async def is_word_exists_in_db(
    word: str,
    conn: asyncpg.Connection,
) -> bool:
    result = await conn.fetch(
        "SELECT word FROM wakabi.words WHERE word = $1",
        word,
    )
    if result:
        return True
    return False


async def _get_word_data_from_db(
    word: str,
    conn: asyncpg.Connection,
) -> list[WordData]:
    results: list[WordData] = []
    count_definitions: int = 0
    rows = await conn.fetch(
        "SELECT definition, pos, word_phonetics, voice_url "
        "FROM wakabi.words WHERE word = $1",
        word,
    )
    if rows:
        for row in rows:
            if count_definitions > MAX_COUNT_DEFINITIONS:
                break
            results.append(
                WordData(
                    word=word,
                    definition=row["definition"],
                    pos=row["pos"],
                    phonetics=row["word_phonetics"],
                    voice_url=row["voice_url"],
                ),
            )
            count_definitions += 1
    return results


def get_word_voice_url(
    word_data: list[WordData],
) -> list[str]:
    word_voice_urls: list[str] = []
    for data in word_data:
        if data.voice_url:
            word_voice_urls.append(data.voice_url)
    return word_voice_urls


async def get_not_found_word_msg(
    word: str,
) -> str:
    return (
        f"Sorry bro, I don't know word: '*{word}*'\\! :\\(\n"
        f"Try find something information in [*chatGPT*]("
        f"{HTTPS_PROTOCOL_STATIC + GPT_CHAT_WEB_URL.format(word=word)})"
    )


def get_network_exception_msg() -> str:
    return formatting.escape_markdown(
        "Sorry, something went wrong... Try again later!",
    )


async def add_new_word_into_db(
    word: str,
    definition: str,
    phonetics: typing.Optional[str],
    pos: typing.Optional[str],
    conn: asyncpg.Connection,
) -> None:
    await conn.execute(
        "INSERT INTO wakabi.words("
        "word, definition, word_phonetics, pos"
        ") VALUES ($1, $2, $3, $4)",
        word,
        definition,
        phonetics,
        pos,
    )


async def get_word_data(
    word: str,
    conn: asyncpg.Connection,
) -> list[WordData]:
    word_data_from_db: list[WordData] = await _get_word_data_from_db(
        word,
        conn,
    )
    if word_data_from_db:
        return word_data_from_db
    word_data_from_dictionary_api: list[
        WordData
    ] = await _get_word_data_from_dictionary_api(
        word,
    )
    return word_data_from_dictionary_api
