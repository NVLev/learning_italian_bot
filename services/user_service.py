from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from model.model import User, UserWordProgress, TrainingSession, Vocabulary
from utils.datetime_utils import now_utc
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def _now() -> datetime:
        """Получить текущее время в UTC"""
        return now_utc()

    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None
    ) -> User:
        """
        Получить существующего пользователя или создать нового.
        
        Args:
            session: Database session
            telegram_id: Telegram user ID
            username: Username (опционально)
            first_name: First name (опционально)
            last_name: Last name (опционально)
            
        Returns:
            User object
        """
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                last_activity_date=UserService._now()
            )
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
                logger.info(f"Created new user: telegram_id={telegram_id}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Error creating user {telegram_id}: {e}")
                raise
        else:
            # Обновляем данные пользователя если они изменились
            if (user.username != username or
                    user.first_name != first_name or
                    user.last_name != last_name):
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                await session.commit()

            # Обновить streak при возвращении
            await UserService._update_streak(session, user)

        return user

    
    @staticmethod
    async def _update_streak(session: AsyncSession, user: User) -> None:
        """
        Обновить streak пользователя.
        Если пользователь приходит каждый день - streak растет.
        Если пропустил день - сбрасывается.
        """
        now = UserService._now()
        
        if not user.last_activity_date:
            user.current_streak = 1
            user.last_activity_date = now
        else:
            days_since_last = (now - user.last_activity_date).days
            
            if days_since_last == 0:
                # Активность в тот же день - ничего не меняем
                pass
            elif days_since_last == 1:
                # Следующий день подряд - увеличиваем streak
                user.current_streak += 1
                user.last_activity_date = now
                
                if user.current_streak > user.longest_streak:
                    user.longest_streak = user.current_streak
            else:
                # Пропустил дни - сброс streak
                user.current_streak = 1
                user.last_activity_date = now
        
        await session.commit()
    
    @staticmethod
    async def get_user_stats(
        session: AsyncSession,
        telegram_id: int
    ) -> dict | None:
        """
        Получить детальную статистику пользователя.
        
        Returns:
            dict с ключами:
            - total_words_learned
            - accuracy (%)
            - current_streak
            - longest_streak
            - level
            - total_trainings
            - words_by_status (new, learning, learned, mastered)
        """
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Подсчет слов по статусам
        words_stats = await session.execute(
            select(
                UserWordProgress.status,
                func.count(UserWordProgress.id)
            )
            .where(UserWordProgress.user_id == user.id)
            .group_by(UserWordProgress.status)
        )
        
        words_by_status = {row[0]: row[1] for row in words_stats}
        
        return {
            'total_words_learned': user.total_words_learned,
            'accuracy': user.accuracy,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'level': user.level,
            'experience_points': user.experience_points,
            'total_trainings': user.total_trainings,
            'total_correct': user.total_correct_answers,
            'total_wrong': user.total_wrong_answers,
            'words_by_status': words_by_status,
            'created_at': user.created_at
        }
    
    @staticmethod
    async def update_word_progress(
        session: AsyncSession,
        user_id: int,
        word_id: int,
        is_correct: bool
    ) -> UserWordProgress:
        """
        Обновить прогресс пользователя по конкретному слову.
        
        Args:
            session: Database session
            user_id: User ID
            word_id: Word ID
            is_correct: Правильно ли ответил пользователь
            
        Returns:
            Updated UserWordProgress object
        """
        result = await session.execute(
            select(UserWordProgress).where(
                UserWordProgress.user_id == user_id,
                UserWordProgress.word_id == word_id
            )
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            progress = UserWordProgress(
                user_id=user_id,
                word_id=word_id,
                status='new',
                first_seen_at=UserService._now(),
                correct_count=0,
                wrong_count=0,
                repetitions=0
            )
            session.add(progress)
            logger.info(f"Created new word progress: user_id={user_id}, word_id={word_id}")

        logger.info(
            f"Current progress: status={progress.status}, correct={progress.correct_count}, wrong={progress.wrong_count}")
        if progress.correct_count is None:
            progress.correct_count = 0
        if progress.wrong_count is None:
            progress.wrong_count = 0
        if progress.repetitions is None:
            progress.repetitions = 0

        # Обновить счетчики
        if is_correct:
            progress.correct_count += 1
            progress.repetitions += 1
        else:
            progress.wrong_count += 1
            progress.repetitions = 0
        old_status = progress.status
        # Обновить статус на основе успешности
        if progress.correct_count >= 3 and progress.status == 'new':
            progress.status = 'learning'
            logger.info(f"Word {word_id} status changed from {old_status} to {progress.status}")
        elif progress.correct_count >= 7 and progress.status == 'learning':
            progress.status = 'learned'
            logger.info(f"Word {word_id} status changed from {old_status} to {progress.status}")
        elif progress.correct_count >= 15 and progress.accuracy > 90:
            progress.status = 'mastered'
            logger.info(f"Word {word_id} status changed from {old_status} to {progress.status}")
        else:
            logger.info(
                f"Word {word_id} status remains {progress.status} (correct={progress.correct_count}, accuracy={progress.accuracy})")
        
        progress.last_reviewed_at = UserService._now()
        
        await session.commit()
        await session.refresh(progress)
        
        # Обновить общую статистику пользователя
        await UserService._update_user_stats(session, user_id, is_correct)
        
        return progress
    
    @staticmethod
    async def _update_user_stats(
        session: AsyncSession,
        user_id: int,
        is_correct: bool
    ) -> None:
        """Обновить общую статистику пользователя"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        if is_correct:
            user.total_correct_answers += 1
        else:
            user.total_wrong_answers += 1
        
        # Подсчитать изученные слова (learned + mastered)
        learned_words_query = select(func.count(UserWordProgress.id)).where(
            UserWordProgress.user_id == user_id,
            UserWordProgress.status.in_(['learned', 'mastered'])
        )
        logger.info(f"Learned words query: {learned_words_query}")
        # --------------------для отладки------------------------------------
        learned_words_result = await session.execute(learned_words_query)
        learned_words_count = learned_words_result.scalar()

        logger.info(f"Found {learned_words_count} learned/mastered words for user {user_id}")

        status_stats = await session.execute(
            select(
                UserWordProgress.status,
                func.count(UserWordProgress.id)
            )
            .where(UserWordProgress.user_id == user_id)
            .group_by(UserWordProgress.status)
        )

        status_counts = {row[0]: row[1] for row in status_stats}
        logger.info(f"Detailed word status counts for user {user_id}: {status_counts}")

        user.total_words_learned = learned_words_count
        logger.info(f"Set total_words_learned to {learned_words_count}")
        # --------------------конец для отладки------------------------------------


        # Добавить опыт
        user.experience_points += 10 if is_correct else 2
        
        # Проверить повышение уровня (каждые 100 очков = +1 уровень)
        new_level = (user.experience_points // 100) + 1
        if new_level > user.level:
            user.level = new_level
            logger.info(f"User {user_id} leveled up to {new_level}!")
        
        await session.commit()
    
    @staticmethod
    async def save_training_session(
        session: AsyncSession,
        user_id: int,
        session_type: str,
        theme_id: int | None,
        correct_answers: int,
        wrong_answers: int,
        duration_seconds: int | None = None
    ) -> TrainingSession:
        """
        Сохранить результаты тренировочной сессии.
        
        Args:
            session: Database session
            user_id: User ID
            session_type: Тип тренировки (quiz, conversation, exercise)
            theme_id: ID темы (опционально)
            correct_answers: Количество правильных ответов
            wrong_answers: Количество неправильных ответов
            duration_seconds: Длительность сессии в секундах
            
        Returns:
            Created TrainingSession object
            :param session:
            :param user_id:
            :param session_type:
            :param theme_id:
            :param correct_answers:
            :param wrong_answers:
            :param duration_seconds:
            :param started_at:
        """
        training = TrainingSession(
            user_id=user_id,
            session_type=session_type,
            theme_id=theme_id,
            total_questions=correct_answers + wrong_answers,
            correct_answers=correct_answers,
            wrong_answers=wrong_answers,
            started_at=UserService._now(),
            completed_at=UserService._now(),
            duration_seconds=duration_seconds
        )
        session.add(training)
        
        # Обновить счетчик тренировок у пользователя
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        user.total_trainings += 1
        
        await session.commit()
        await session.refresh(training)
        
        logger.info(f"Saved training session for user {user_id}: {session_type}")
        
        return training
    
    @staticmethod
    async def get_words_for_review(
        session: AsyncSession,
        user_id: int,
        limit: int = 10
    ) -> list[Vocabulary]:
        """
        Получить слова для повторения (Spaced Repetition).
        
        Args:
            session: Database session
            user_id: User ID
            limit: Максимальное количество слов
            
        Returns:
            List of Vocabulary objects
        """
        now = UserService._now()
        
        result = await session.execute(
            select(Vocabulary)
            .join(UserWordProgress)
            .where(
                UserWordProgress.user_id == user_id,
                UserWordProgress.next_review_date <= now,
                UserWordProgress.status.in_(['learning', 'learned'])
            )
            .order_by(UserWordProgress.next_review_date)
            .limit(limit)
        )
        
        return list(result.scalars().all())


    
