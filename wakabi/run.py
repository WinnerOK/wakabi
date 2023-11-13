import asyncio

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter
from telebot.types import CallbackQuery

from wakabi.settings import Settings
from wakabi.tg_bot import callbacks, handlers


def register_handlers(bot: AsyncTeleBot) -> None:
    bot.register_message_handler(
        handlers.start_handler,
        commands=["start"],
        pass_bot=True,
    )
    bot.register_message_handler(
        handlers.training_handler,
        commands=["training"],
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        callbacks.language_level_callback,
        func=None,
        config=callbacks.language_level_data.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        callbacks.training_callback,
        func=None,
        config=callbacks.training_data.filter(),
        pass_bot=True,
    )


class CallbackFilter(AdvancedCustomFilter):
    key = "config"

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


def main():
    settings = Settings()
    bot = AsyncTeleBot(settings.telegram_token)
    bot.settings = settings
    bot.add_custom_filter(CallbackFilter())
    register_handlers(bot)

    asyncio.run(bot.polling())


if __name__ == "__main__":
    main()
