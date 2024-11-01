from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column

Base = declarative_base()


class Theme(Base):
    """Модель для описания темы"""
    __tablename__ = 'themes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), unique=True)


class Vocabulary(Base):
    """Модель словаря, с привязкой к темам"""
    __tablename__ = 'vocabulary'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    italian_word: Mapped[str] = mapped_column(String(50))
    rus_word: Mapped[str] = mapped_column(String(50))
    theme_id: Mapped[str] = mapped_column(Integer, ForeignKey('themes.id'))


# Database connection
