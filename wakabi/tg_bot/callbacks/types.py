from enum import Enum

from telebot.callback_data import CallbackData

language_level_data = CallbackData("level", prefix="lang_level")


class TrainingExerciseStatus(str, Enum):
    passed = "pass"
    fail = "fail"


training_iteration_start_data = CallbackData(  # строка 64 байта
    # "status",
    "word_id",
    "correct_count",
    "incorrect_count",
    prefix="tr_st",  # сделать короче
)


training_iteration_end_data = CallbackData(  # code duplication
    "status",
    "word_id",
    "correct_count",
    "incorrect_count",
    prefix="tr_end",
)


exit_training_data = CallbackData(
    "correct_count",
    "incorrect_count",
    prefix="exit_training",
)


word_discovery_data = CallbackData("word_id", prefix="word_disc")
