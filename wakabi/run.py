import asyncio

from telebot.async_telebot import AsyncTeleBot

from wakabi.settings import Settings
from wakabi.tg_bot import handlers


def register_handlers(bot: AsyncTeleBot) -> None:
    bot.register_message_handler(
        handlers.start_handler,
        commands=["start"],
        pass_bot=True,
    )


def main():
    settings = Settings()
    bot = AsyncTeleBot(settings.telegram_token)
    register_handlers(bot)

    asyncio.run(bot.polling())


if __name__ == "__main__":
    main()
