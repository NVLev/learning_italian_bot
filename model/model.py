from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    Модель пользователя бота.
    Хранит базовую информацию и общую статистику.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))

    total_words_learned: Mapped[int] = mapped_column(Integer, default=0)
    total_correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_wrong_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_trainings: Mapped[int] = mapped_column(Integer, default=0)

    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[datetime | None] = mapped_column(DateTime)

    level: Mapped[int] = mapped_column(Integer, default=1)
    experience_points: Mapped[int] = mapped_column(Integer, default=0)

    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_difficulty: Mapped[str | None] = mapped_column(String(20))  # easy, medium, hard

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    word_progress = relationship("UserWordProgress", back_populates="user", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="user", cascade="all, delete-orphan")

    @property
    def accuracy(self) -> float:
        """Процент правильных ответов"""
        total = self.total_correct_answers + self.total_wrong_answers
        if total == 0:
            return 0.0
        return round((self.total_correct_answers / total) * 100, 2)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class Theme(Base):
    """Модель для описания темы"""
    __tablename__ = 'themes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), unique=True)

    words = relationship("Vocabulary", back_populates="theme")
    training_sessions = relationship("TrainingSession", back_populates="theme")

    def __repr__(self):
        return f"<Theme(name={self.name})>"


class Vocabulary(Base):
    """Модель словаря, с привязкой к темам"""
    __tablename__ = 'vocabulary'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    italian_word: Mapped[str] = mapped_column(String(50))
    rus_word: Mapped[str] = mapped_column(String(50))
    theme_id: Mapped[str] = mapped_column(Integer, ForeignKey('themes.id'))

    # Дополнительная информация
    difficulty: Mapped[str | None] = mapped_column(String(20))  # easy, medium, hard
    usage_example: Mapped[str | None] = mapped_column(String(500))

    theme = relationship("Theme", back_populates="words")
    user_progress = relationship("UserWordProgress", back_populates="word")

    def __repr__(self):
        return f"<Vocabulary(italian={self.italian_word}, russian={self.rus_word})>"


class UserWordProgress(Base):
    """
    Прогресс пользователя по каждому слову.
    Отслеживает уровень знания и историю повторений.
    """
    __tablename__ = 'user_word_progress'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey('vocabulary.id', ondelete='CASCADE'), index=True)

    # Статус изучения
    status: Mapped[str] = mapped_column(String(20), default='new')  # new, learning, learned, mastered

    # Статистика по слову
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)

    # Spaced Repetition (SM-2 алгоритм)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)  # Количество успешных повторений
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5)  # Фактор легкости (1.3-2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)  # Интервал до следующего повторения
    next_review_date: Mapped[datetime | None] = mapped_column(DateTime)  # Когда нужно повторить

    # Временные метки
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    user = relationship("User", back_populates="word_progress")
    word = relationship("Vocabulary", back_populates="user_progress")

    # Уникальность: один пользователь - одно слово
    __table_args__ = (
        {'schema': None},
    )

    @property
    def accuracy(self) -> float:
        """Процент правильных ответов для этого слова"""
        total = self.correct_count + self.wrong_count
        if total == 0:
            return 0.0
        return round((self.correct_count / total) * 100, 2)

    def __repr__(self):
        return f"<UserWordProgress(user_id={self.user_id}, word_id={self.word_id}, status={self.status})>"


class TrainingSession(Base):
    """
    История тренировочных сессий пользователя.
    Позволяет отслеживать активность и прогресс во времени.
    """
    __tablename__ = 'training_sessions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)

    session_type: Mapped[str] = mapped_column(String(50))  # quiz, conversation, exercise
    theme_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('themes.id'))

    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    wrong_answers: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)  # Длительность сессии

    user = relationship("User", back_populates="training_sessions")
    theme = relationship("Theme", back_populates="training_sessions")

    @property
    def accuracy(self) -> float:
        """Точность в этой сессии"""
        if self.total_questions == 0:
            return 0.0
        return round((self.correct_answers / self.total_questions) * 100, 2)

    def __repr__(self):
        return f"<TrainingSession(user_id={self.user_id}, type={self.session_type}, accuracy={self.accuracy}%)>"


class Idiom(Base):
    """Модель итальянских идиом с переводом на русский"""
    __tablename__ = 'idiom'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    italian_idiom: Mapped[str]= mapped_column(String)
    rus_idiom: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"<Idiom(italian={self.italian_idiom[:30]}...)>"


