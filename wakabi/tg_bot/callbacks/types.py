from enum import Enum

from telebot.callback_data import CallbackData

language_level_data = CallbackData("level", prefix="lang_level")


class TrainingExerciseStatus(str, Enum):
    passed = "pass"
    fail = "fail"


training_data = CallbackData(
    "status",
    "word_id",
    "correct_count",
    "incorrect_count",
    prefix="tr",
)
