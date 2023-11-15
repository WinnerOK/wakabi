from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from wakabi.tg_bot.callbacks.types import (
    TrainingExerciseStatus,
    language_level_data,
    training_data,
    word_discovery_data,
)


def language_level_markup() -> InlineKeyboardMarkup:
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        *[
            InlineKeyboardButton(
                text=level,
                callback_data=language_level_data.new(level=level),
            )
            for level in levels
        ],
        row_width=2,
    )
    return keyboard


def training_markup(
    word_id: int,  # TODO(mr-nikulin): replace with word (str)
    correct_count: int = 0,
    incorrect_count: int = 0,
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton(
            text="Знаю ✅",
            callback_data=training_data.new(
                status=TrainingExerciseStatus.passed,
                word_id=word_id,
                correct_count=correct_count + 1,
                incorrect_count=incorrect_count,
            ),
        ),
        InlineKeyboardButton(
            text="Не знаю ❌",
            callback_data=training_data.new(
                status=TrainingExerciseStatus.fail,
                word_id=word_id,
                correct_count=correct_count,
                incorrect_count=incorrect_count + 1,
            ),
        ),
    )
    return keyboard


def add_to_vocabulary_markup(word_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="Добавить в словарь🔎",
            callback_data=word_discovery_data.new(
                word_id=word_id,
            ),
        ),
    )
    return keyboard
