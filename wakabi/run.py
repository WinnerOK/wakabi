import asyncio

from functools import partial

import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter
from telebot.types import CallbackQuery

from wakabi.settings import Settings
from wakabi.tg_bot import callbacks, handlers


def register_handlers(bot: AsyncTeleBot, pool: asyncpg.Pool) -> None:
    bot.register_message_handler(
        handlers.start_handler,
        commands=["start"],
        pass_bot=True,
    )
    bot.register_message_handler(
        # handlers.training_handler,
        partial(
            handlers.training_handler,
            pool=pool,
        ),
        commands=["training"],
        pass_bot=True,
    )
    bot.register_message_handler(
        handlers.help_handler,
        commands=["help"],
        pass_bot=True,
    )

    bot.register_message_handler(
        partial(
            handlers.definition_handler,
            pool=pool,
        ),
        pass_bot=True,
    )

    bot.register_message_handler(
        partial(
            handlers.file_handler,
            pool=pool,
        ),
        content_types=["document"],
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            callbacks.language_level_callback,
            pool=pool,
        ),
        func=None,
        config=callbacks.language_level_data.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            callbacks.training_iteration_start_callback,
            pool=pool,
        ),
        func=None,
        config=callbacks.training_iteration_start_data.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            callbacks.training_iteration_end_callback,
            pool=pool,
        ),
        func=None,
        config=callbacks.training_iteration_end_data.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        callbacks.exit_training_callback,
        func=None,
        config=callbacks.exit_training_data.filter(),  # correct_count = 3
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            callbacks.save_discovered_word_callback,
            pool=pool,
        ),
        func=None,
        config=callbacks.word_discovery_data.filter(),
        pass_bot=True,
    )


class CallbackFilter(AdvancedCustomFilter):
    key = "config"

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


async def main():
    settings = Settings()

    try:
        pool: asyncpg.Pool = await asyncio.wait_for(
            asyncpg.create_pool(
                dsn=str(settings.pg_dsn),
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError as e:
        msg = "Couldn't connect to database"
        raise RuntimeError(msg) from e

    bot = AsyncTeleBot(settings.telegram_token)
    bot.settings = settings
    bot.add_custom_filter(CallbackFilter())
    register_handlers(bot, pool)
    await bot.delete_my_commands()
    await bot.set_my_commands(handlers.BOT_COMMANDS)

    try:
        await bot.polling()
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
