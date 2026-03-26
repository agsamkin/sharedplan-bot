from aiogram.fsm.state import State, StatesGroup


class CreateSpace(StatesGroup):
    waiting_for_name = State()
