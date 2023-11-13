from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from wakabi.tg_bot.callbacks import language_level


def language_level_markup() -> InlineKeyboardMarkup:
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        *[
            InlineKeyboardButton(
                text=level,
                callback_data=language_level.new(level=level),
            )
            for level in levels
        ],
        row_width=2,
    )
    return keyboard
