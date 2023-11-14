import telebot.formatting as fmt

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from wakabi.tg_bot.markups import add_to_vocabulary_markup


async def discovery_handler(message: Message, bot: AsyncTeleBot):
    unknown_expression = message.text.strip().lower()
    # TODO: search for expression in DB
    found = not unknown_expression.endswith("_no")
    if found:
        word_id = 1
        definition = "is a wonderful term that I will definitely explain"

        await bot.reply_to(
            message,
            fmt.format_text(
                fmt.mbold(unknown_expression),
                definition,
                separator=" ",
            ),
            parse_mode="MarkdownV2",
            reply_markup=add_to_vocabulary_markup(word_id),
        )
        return

    await bot.reply_to(
        message,
        fmt.format_text(
            fmt.escape_markdown("Unfortunately I don't have a definition for"),
            fmt.mbold(unknown_expression),
            separator=" ",
        ),
        parse_mode="MarkdownV2",
    )
