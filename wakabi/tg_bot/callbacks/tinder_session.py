import asyncpg
import telebot.formatting as fmt

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

import wakabi.repository.tinder_session as tinder_repo
import wakabi.repository.user as user_repo

from wakabi.tg_bot.callbacks.types import TinderSessionAction, tinder_session_data
from wakabi.tg_bot.markups import word_tinder_markup


async def finish_tinder_session(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = tinder_session_data.parse(callback_data=call.data)

    async with pool.acquire() as conn:  # type: asyncpg.Connection
        await tinder_repo.stop_session(conn, int(callback_data["session_id"]))

    await bot.edit_message_text(
        "Finished session",
        chat_id=call.message.chat.id,
        message_id=call.message.id,
    )


async def process_tinder_session_choice(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = tinder_session_data.parse(callback_data=call.data)

    async with pool.acquire() as conn:  # type: asyncpg.Connection
        async with conn.transaction():
            if callback_data["action"] == TinderSessionAction.add:
                await user_repo.add_word_to_learn(
                    conn,
                    call.from_user.id,
                    callback_data["word"],
                )

            next_word = await tinder_repo.get_next_word_from_session(
                conn,
                int(callback_data["session_id"]),
            )

    if not next_word:
        await bot.edit_message_text(
            "Finished session",
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
        return

    await bot.edit_message_text(
        f"Word {fmt.mbold(next_word)}\n\nWould you add this?",
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=word_tinder_markup(
            session_id=callback_data["session_id"],
            word=next_word,
        ),
        parse_mode="MarkdownV2",
    )
