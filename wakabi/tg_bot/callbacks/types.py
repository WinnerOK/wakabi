from enum import Enum

from telebot.callback_data import CallbackData

language_level_data = CallbackData("level", prefix="lang_level")


class TrainingExerciseStatus(str, Enum):
    passed = "pass"
    fail = "fail"


training_iteration_start_data = CallbackData(
    "word_id",
    "correct_count",
    "incorrect_count",
    prefix="tr_st",
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
    prefix="ex_tr",
)

word_discovery_data = CallbackData("word", prefix="add_w")

tinder_session_data = CallbackData("session_id", "word", "action", prefix="td_s")


class TinderSessionAction(str, Enum):
    add = "add"
    skip = "skip"
    finish = "finish"
