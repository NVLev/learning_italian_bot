from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Theme схемы
class ThemeBase(BaseModel):
    name: str


class ThemeCreate(ThemeBase):
    pass


class ThemeRead(ThemeBase):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# Vocabulary схемы
class VocabularyBase(BaseModel):
    italian_word: str
    rus_word: str
    theme_id: int


class VocabularyCreate(VocabularyBase):
    difficulty: Optional[str] = None
    usage_example: Optional[str] = None


class VocabularyRead(VocabularyBase):
    id: int
    italian_word: str
    rus_word: str
    theme_id: int
    difficulty: Optional[str] = None
    usage_example: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Idiom схемы
class IdiomBase(BaseModel):
    italian_idiom: str
    rus_idiom: str


class IdiomCreate(IdiomBase):
    pass


class IdiomRead(IdiomBase):
    id: int
    italian_idiom: str
    rus_idiom: str

    model_config = ConfigDict(from_attributes=True)


# User схемы
class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    total_words_learned: int = 0
    total_correct_answers: int = 0
    total_wrong_answers: int = 0
    total_trainings: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    level: int = 1
    experience_points: int = 0
    notifications_enabled: bool = True
    preferred_difficulty: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserStats(BaseModel):
    total_words_learned: int
    accuracy: float
    current_streak: int
    longest_streak: int
    level: int
    experience_points: int
    total_trainings: int
    total_correct: int
    total_wrong: int
    words_by_status: dict
    created_at: datetime


# UserWordProgress схемы
class UserWordProgressBase(BaseModel):
    user_id: int
    word_id: int
    status: str = 'new'


class UserWordProgressCreate(UserWordProgressBase):
    pass


class UserWordProgressRead(UserWordProgressBase):
    id: int
    user_id: int
    word_id: int
    status: str
    correct_count: int = 0
    wrong_count: int = 0
    repetitions: int = 0
    easiness_factor: float = 2.5
    interval_days: int = 0
    first_seen_at: datetime
    last_reviewed_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# TrainingSession схемы
class TrainingSessionBase(BaseModel):
    user_id: int
    session_type: str
    theme_id: Optional[int] = None


class TrainingSessionCreate(TrainingSessionBase):
    correct_answers: int = 0
    wrong_answers: int = 0
    duration_seconds: Optional[int] = None


class TrainingSessionRead(TrainingSessionBase):
    id: int
    user_id: int
    session_type: str
    theme_id: Optional[int] = None
    total_questions: int = 0
    correct_answers: int = 0
    wrong_answers: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# Response схемы для API
class UserWithProgress(BaseModel):
    user: UserRead
    word_progress: List[UserWordProgressRead]
    training_sessions: List[TrainingSessionRead]