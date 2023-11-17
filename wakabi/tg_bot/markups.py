from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from wakabi.tg_bot.callbacks.types import (
    TinderSessionAction,
    TrainingExerciseStatus,
    exit_training_data,
    language_level_data,
    tinder_session_data,
    training_iteration_end_data,
    training_iteration_start_data,
    word_discovery_data,
)


def language_level_markup() -> InlineKeyboardMarkup:
    levels = ("A1", "A2", "B1", "B2", "C1", "C2")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        *[
            InlineKeyboardButton(
                text=level,
                callback_data=language_level_data.new(level=level.lower()),
            )
            for level in levels
        ],
        row_width=2,
    )
    return keyboard


def training_iteration_start_markup(
    word_id: int,
    correct_count: int = 0,
    incorrect_count: int = 0,
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton(
            text="Don't know ❌",
            callback_data=training_iteration_end_data.new(
                status=TrainingExerciseStatus.fail,
                word_id=word_id,
                correct_count=correct_count,
                incorrect_count=incorrect_count + 1,
            ),
        ),
        InlineKeyboardButton(
            text="Know ✅",
            callback_data=training_iteration_end_data.new(
                status=TrainingExerciseStatus.passed,
                word_id=word_id,
                correct_count=correct_count + 1,
                incorrect_count=incorrect_count,
            ),
        ),
        InlineKeyboardButton(
            text="Finish 🏁",
            callback_data=exit_training_data.new(
                correct_count=correct_count,
                incorrect_count=incorrect_count,
            ),
        ),
    )
    return keyboard


def training_iteration_end_markup(
    status: TrainingExerciseStatus,
    correct_count: int,
    incorrect_count: int,
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton(
            text="Finish 🏁",
            callback_data=exit_training_data.new(
                correct_count=correct_count,
                incorrect_count=incorrect_count,
            ),
        ),
        InlineKeyboardButton(
            text="Next ➡️",
            callback_data=training_iteration_start_data.new(
                previous_status=status,
                correct_count=correct_count,
                incorrect_count=incorrect_count,
            ),
        ),
    )
    return keyboard


def add_to_vocabulary_markup(word: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="Save for trainings 🔎",
            callback_data=word_discovery_data.new(
                word=word,
            ),
        ),
    )
    return keyboard


def word_tinder_markup(session_id: int, word: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton(
            text="Skip ❌",
            callback_data=tinder_session_data.new(
                session_id=session_id,
                word=word,
                action=TinderSessionAction.skip,
            ),
        ),
        InlineKeyboardButton(
            text="Add to dict 💚",
            callback_data=tinder_session_data.new(
                session_id=session_id,
                word=word,
                action=TinderSessionAction.add,
            ),
        ),
        InlineKeyboardButton(
            text="Finish 🏁",
            callback_data=tinder_session_data.new(
                session_id=session_id,
                word=word,
                action=TinderSessionAction.finish,
            ),
        ),
    )
    return keyboard
