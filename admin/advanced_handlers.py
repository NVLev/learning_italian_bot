from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import random
from services.conversation_service import ConversationService
from services.exercise_service import ExerciseService
from reply_keyboard.rep_kb import main_kb
import logging

logger = logging.getLogger(__name__)

router = Router()
conversation_service = ConversationService()
exercise_service = ExerciseService()


class ConversationStates(StatesGroup):
    waiting_for_reply = State()


class ExerciseStates(StatesGroup):
    waiting_for_gap_answer = State()
    waiting_for_quiz_answer = State()


# Диалоговый режим
@router.message(Command("conversation"))
@router.message(F.text == "💬 Практика диалога")
async def start_conversation_handler(message: Message, state: FSMContext):
    """Начало диалоговой практики"""
    if not conversation_service.enabled:
        await message.answer("❌ Диалоговый режим временно недоступен")
        return

    italian_phrase, russian_translation = await conversation_service.start_conversation()

    await message.answer(
        f"🇮🇹 **Давайте попрактикуем итальянский!**\n\n"
        f"Преподаватель: {italian_phrase}\n"
        f"📖 Перевод: {russian_translation}\n\n"
        f"*Ответьте на итальянском:*",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Завершить диалог")]],
            resize_keyboard=True
        )
    )

    # Сохраняем историю диалога
    await state.update_data(
        conversation_history=[{"role": "assistant", "content": italian_phrase}]
    )
    await state.set_state(ConversationStates.waiting_for_reply)


@router.message(ConversationStates.waiting_for_reply)
async def handle_conversation_reply(message: Message, state: FSMContext):
    """Обработка ответа в диалоге"""
    if message.text == "❌ Завершить диалог":
        await message.answer("Диалог завершен!", reply_markup=main_kb())
        await state.clear()
        return

    user_data = await state.get_data()
    conversation_history = user_data.get("conversation_history", [])

    italian_response, russian_translation, new_history, correction = await conversation_service.continue_conversation(
        message.text, conversation_history
    )

    response_text = f"🇮🇹 Преподаватель: {italian_response}\n📖 Перевод: {russian_translation}"
    if correction:
        response_text += f"\n\n🔍 Исправление: {correction}"

    await message.answer(response_text)

    await state.update_data(conversation_history=new_history)


# Упражнения
@router.message(Command("exercise"))
@router.message(F.text == "📝 Упражнения")
async def send_exercise(message: Message, state: FSMContext):
    """Отправка случайного упражнения"""
    if not exercise_service.enabled:
        await message.answer("❌ Сервис упражнений временно недоступен")
        return

    # Случайно выбираем тип упражнения
    exercise_type = random.choice(["gap_fill", "quiz"])

    if exercise_type == "gap_fill":
        exercise = await exercise_service.generate_gap_exercise()
        if exercise:
            await message.answer(
                f"🔤 **Упражнение: Заполните пропуски**\n\n"
                f"{exercise['exercise']}\n\n"
                f"*Введите ответы через запятую:*",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="❌ Пропустить упражнение")]],
                    resize_keyboard=True
                )
            )
            await state.update_data(current_exercise=exercise)
            await state.set_state(ExerciseStates.waiting_for_gap_answer)
        else:
            await message.answer("❌ Не удалось создать упражнение", reply_markup=main_kb())

    else:  # quiz
        exercise = await exercise_service.generate_quiz()
        if exercise:
            # Создаем клавиатуру с вариантами ответов
            kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="A"), KeyboardButton(text="B")],
                    [KeyboardButton(text="C"), KeyboardButton(text="D")],
                    [KeyboardButton(text="❌ Пропустить упражнение")]
                ],
                resize_keyboard=True
            )

            await message.answer(
                f"❓ **Викторина**\n\n{exercise['question']}",
                reply_markup=kb
            )
            await state.update_data(current_exercise=exercise)
            await state.set_state(ExerciseStates.waiting_for_quiz_answer)
        else:
            await message.answer("❌ Не удалось создать викторину", reply_markup=main_kb())


@router.message(ExerciseStates.waiting_for_gap_answer)
async def check_gap_answer(message: Message, state: FSMContext):
    """Проверка ответа на упражнение с пропусками"""
    if message.text == "❌ Пропустить упражнение":
        await message.answer("Упражнение пропущено", reply_markup=main_kb())
        await state.clear()
        return

    user_data = await state.get_data()
    exercise = user_data.get("current_exercise")

    if exercise:
        user_answers = [ans.strip().lower() for ans in message.text.split(",")]
        correct_answers = [ans.strip().lower() for ans in exercise['answers']]

        if user_answers == correct_answers:
            response = "✅ **Правильно!** Отличная работа!\n\n"
        else:
            response = "❌ **Есть ошибки.** Правильные ответы:\n"
            response += ", ".join(exercise['answers']) + "\n\n"

        response += f"📖 Перевод: {exercise['translation']}"

        await message.answer(response, reply_markup=main_kb())

        # ❗ Вместо state.clear() — запускаем следующее упражнение
        await send_exercise(message, state)


@router.message(ExerciseStates.waiting_for_quiz_answer)
async def check_quiz_answer(message: Message, state: FSMContext):
    """Проверка ответа на викторину"""
    if message.text == "❌ Пропустить упражнение":
        await message.answer("Викторина пропущена", reply_markup=main_kb())
        await state.clear()
        return

    user_data = await state.get_data()
    exercise = user_data.get("current_exercise")

    if exercise:
        if message.text.strip().lower().startswith(exercise['correct_answer'].strip().lower()):
            response = "✅ **Правильно!** Отличная работа!\n\n"
        else:
            response = f"❌ **Неправильно.** Правильный ответ: {exercise['correct_answer']}\n\n"

        response += f"💡 Объяснение: {exercise['explanation']}"

        await message.answer(response, reply_markup=main_kb())

        # ❗ Вместо state.clear() — запускаем следующее упражнение
        await send_exercise(message, state)

# Обработчики для новых пунктов меню
@router.message(F.text == "💬 Практика диалога (AI)")
async def conversation_menu_handler(message: Message, state: FSMContext):
    """Обработчик кнопки 'Практика диалога (AI)' из меню"""
    await start_conversation_handler(message, state)

@router.message(F.text == "📝 Упражнения (AI)")
async def exercises_menu_handler(message: Message, state: FSMContext):
    """Обработчик кнопки 'Упражнения (AI)' из меню"""
    await send_exercise(message, state)

