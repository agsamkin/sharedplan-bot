from aiogram.fsm.state import State, StatesGroup


class EditEvent(StatesGroup):
    waiting_for_value = State()
    waiting_for_confirm = State()
