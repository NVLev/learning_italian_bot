"""
Handlers для отображения статистики пользователя.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from services.user_service import UserService
from reply_keyboard.rep_kb import main_kb
from model.model import User
from config_data.config import logger



router = Router()


@router.message(Command("stats"))
@router.message(F.text == "📊 Моя статистика")
async def cmd_stats(message: Message, db_user: User, session):
    """
    Показать статистику пользователя.

    Args:
        db_user: User object (из middleware)
        session: Database session (из middleware)
    """
    try:
        stats = await UserService.get_user_stats(
            session=session,
            telegram_id=message.from_user.id
        )

        if not stats:
            await message.answer("❌ Статистика не найдена")
            return

        words_by_status = stats.get('words_by_status', {})

        response = (
            f"📊 **Твоя статистика**\n\n"
            f"👤 Уровень: {stats['level']} "
            f"(⭐ {stats['experience_points']} XP)\n\n"

            f"📚 **Слова:**\n"
            f"• Изучено: {stats['total_words_learned']}\n"
            f"• Новые: {words_by_status.get('new', 0)}\n"
            f"• Изучаются: {words_by_status.get('learning', 0)}\n"
            f"• Выучены: {words_by_status.get('learned', 0)}\n"
            f"• Освоены: {words_by_status.get('mastered', 0)}\n\n"

            f"🎯 **Точность:** {stats['accuracy']:.1f}%\n"
            f"✅ Правильных: {stats['total_correct']}\n"
            f"❌ Ошибок: {stats['total_wrong']}\n\n"

            f"🔥 **Streak:** {stats['current_streak']} дней подряд\n"
            f"🏆 Лучший: {stats['longest_streak']} дней\n\n"

            f"📝 Всего тренировок: {stats['total_trainings']}\n"
        )

        await message.answer(response, parse_mode="Markdown", reply_markup=main_kb())

    except Exception as e:
        logger.error(f"Error in cmd_stats: {e}")
        await message.answer("❌ Ошибка при получении статистики")


@router.message(Command("level"))
async def cmd_level(message: Message, db_user: User):
    """
    Показать информацию об уровне.

    Args:
        db_user: User object (из middleware)
    """
    # Рассчитываем прогресс до следующего уровня
    next_level_xp = db_user.level * 100
    current_level_xp = (db_user.level - 1) * 100
    progress_xp = db_user.experience_points - current_level_xp
    needed_xp = next_level_xp - db_user.experience_points

    # Прогресс-бар
    progress_percent = (progress_xp / 100) * 100
    progress_bar = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))

    response = (
        f"⭐ **Уровень {db_user.level}**\n\n"
        f"Опыт: {db_user.experience_points} XP\n"
        f"До следующего уровня: {needed_xp} XP\n\n"
        f"Прогресс:\n{progress_bar} {progress_percent:.0f}%\n\n"
        f"💡 Получай опыт за:\n"
        f"• Правильный ответ: +10 XP\n"
        f"• Попытка (даже ошибка): +2 XP\n"
        f"• Новый уровень каждые 100 XP"
    )

    await message.answer(response, parse_mode="Markdown")


@router.message(Command("streak"))
@router.message(F.text == "🔥 Мой streak")
async def cmd_streak(message: Message, db_user: User):
    """
    Показать информацию о streak.

    Args:
        db_user: User object (из middleware)
    """
    # Эмодзи в зависимости от streak
    if db_user.current_streak >= 30:
        emoji = "🔥🔥🔥"
    elif db_user.current_streak >= 7:
        emoji = "🔥🔥"
    elif db_user.current_streak >= 3:
        emoji = "🔥"
    else:
        emoji = "💪"

    response = (
        f"{emoji} **Твой Streak**\n\n"
        f"Текущий: {db_user.current_streak} дней подряд\n"
        f"Лучший результат: {db_user.longest_streak} дней\n\n"
    )

    if db_user.current_streak == 0:
        response += "💡 Начни тренироваться сегодня, чтобы создать streak!"
    elif db_user.current_streak < 7:
        response += f"💪 Ещё {7 - db_user.current_streak} дней до недели подряд!"
    elif db_user.current_streak < 30:
        response += f"🎯 Ещё {30 - db_user.current_streak} дней до месяца!"
    else:
        response += "🏆 Невероятно! Ты настоящий мастер!"

    await message.answer(response, parse_mode="Markdown")