from aiogram.fsm.state import State, StatesGroup


class CreateEvent(StatesGroup):
    waiting_for_space = State()
    waiting_for_confirm = State()
    waiting_for_edit = State()
    waiting_for_past_confirm = State()
