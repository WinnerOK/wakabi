import typing

import enum
import re

import aiohttp
import asyncpg

HTTPS_PROTOCOL_STATIC = "https://"
DICTIONARY_API_URL = "api.dictionaryapi.dev/api/v2/entries/en/{word}"
GPT_CHAT_WEB_URL = "you.com/search?q={word}"
YANDEX_IMAGES_WEB_URL = "yandex.ru/images/search?text={word}"
YOUGLISH_ENGLISH_WEB_URL = "youglish.com/pronounce/{word}/english"

NO_DEFINITIONS_FOUND_API_MSG = "No Definitions Found"

MAX_COUNT_DEFINITIONS = 3

BRACKETS_SANITIZER_PATTERN = r"\(.*?\)|\."
SPACE_SANITIZER_PATTERN = r"^\s+|\s+$"
SPECIALIZED_SYMBOLS_PATTERN = r"([.?!\-])"


class NetworkException(Exception):
    pass


class DefinitionFields(enum.Enum):
    DEFINITION = "definition"
    DEFINITIONS = "definitions"
    MEANINGS = "meanings"
    PART_OF_SPEACH = "partOfSpeech"


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


def get_word_definition_formatted(
    word: str,
    word_definition_raw: str,
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
    word_definition_formatted: str = (
        f"*Определение* слова *{word}*:\n{word_definition_raw}\n"
        f"Полезное *медиа*: \n"
        f"[Look at images by word *{word}*\\!]({yandex_content_by_word}) \n"
        rf"[Train your pronunciation for word *{word}*\!]"
        f"({youglish_content_by_word})\n"
    )
    return word_definition_formatted


async def _get_word_definition_from_dictionary_api(
    word: str,
) -> typing.Optional[str]:
    definitions: list[str] = []
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
                    return None
                for definition in data[0][DefinitionFields.MEANINGS.value]:
                    if count_definitions > MAX_COUNT_DEFINITIONS:
                        break
                    word_part_of_speech = _format_string(
                        definition[DefinitionFields.PART_OF_SPEACH.value],
                    )
                    word_definition_prepared = _format_string(
                        definition[DefinitionFields.DEFINITIONS.value][0][
                            DefinitionFields.DEFINITION.value
                        ],
                    )
                    definitions.append(
                        "*"
                        + word_part_of_speech
                        + "*"
                        + "; "
                        + word_definition_prepared
                        + ";"
                        + "\n",
                    )
                    count_definitions += 1
                return "".join(definitions)
        except Exception:
            raise NetworkException


async def is_word_exists_in_db(
    word: str,
    pool: asyncpg.Pool,
) -> bool:
    async with pool.acquire() as conn:
        result = await conn.fetch(
            "SELECT word FROM wakabi.words WHERE word = $1",
            word,
        )
        if result:
            return True
    return False


async def _get_word_definition_from_db(
    word: str,
    pool: asyncpg.Pool,
) -> typing.Optional[str]:
    count_definitions: int = 0
    results: list[str] = []
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT word_phonetics, "
            "pos, definition FROM wakabi.words WHERE word = $1",
            word,
        )
        if rows:
            for row in rows:
                if count_definitions > MAX_COUNT_DEFINITIONS:
                    break
                res_prepared = ""
                if row["pos"]:
                    res_prepared += "*" + _format_string(row["pos"]) + "*" + "; "
                if row["word_phonetics"]:
                    res_prepared += _format_string(row["word_phonetics"]) + "; "
                res_prepared += _format_string(row["definition"]) + "\n"
                results.append(
                    res_prepared,
                )
                count_definitions += 1
            return "".join(results)
    return None


async def get_not_found_word_msg(
    word: str,
) -> str:
    return (
        f"Sorry bro, I don't know word: '*{word}*'\\! :\\(\n"
        f"Try find something information in [*chatGPT*]("
        f"{HTTPS_PROTOCOL_STATIC + GPT_CHAT_WEB_URL.format(word=word)})"
    )


def get_network_exception_msg() -> str:
    return "Sorry, something went wrong... Try again later!"


async def add_new_word_into_db(
    word: str,
    definition: str,
    pool: asyncpg.Pool,
) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO wakabi.words(word, definition) VALUES ($1, $2)",
            word,
            definition,
        )


async def get_word_definition(
    word: str,
    pool: asyncpg.Pool,
) -> typing.Optional[str]:
    word_definition_from_db: typing.Optional[str] = await _get_word_definition_from_db(
        word,
        pool,
    )
    if word_definition_from_db:
        return word_definition_from_db
    word_definition_from_dictionary_api: typing.Optional[
        str
    ] = await _get_word_definition_from_dictionary_api(
        word,
    )
    return word_definition_from_dictionary_api
