from aiogram.fsm.state import State, StatesGroup


class AvailableStates(StatesGroup):
    process_user_word_answer = State()
    awaiting_file_upload = State()
    awaiting_previous_file_upload = State()
    waiting_for_promocode = State()
