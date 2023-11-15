import typing

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi import definition


async def definition_handler(message: Message, bot: AsyncTeleBot, connection):
    word: str = message.text
    try:
        word_definition_raw: typing.Optional[
            str
        ] = await definition.get_word_definition(
            word
        )
    except definition.NetworkException:
        bot_msg = definition.get_network_exception_msg()
        await bot.send_message(
            chat_id=message.chat.id,
            text=bot_msg,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
        return
    if word_definition_raw:
        word_definition_formatted: str = (
            definition.get_word_definition_formatted(
                word=word,
                word_definition_raw=word_definition_raw,
            )
        )
        bot_msg = word_definition_formatted
    else:
        bot_msg = await definition.get_not_found_word_msg(word)
    await bot.send_message(
        chat_id=message.chat.id,
        text=bot_msg,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )
    if not await definition.is_word_exists_in_db(word):
        await definition.add_new_word_into_db(
            word=word,
            definition=word_definition_raw,
        )





