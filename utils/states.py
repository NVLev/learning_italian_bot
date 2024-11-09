from aiogram.fsm.state import StatesGroup, State

class Quiz(StatesGroup):
    idiom = State()
    no_quiz = State()
    quiz_start = State()