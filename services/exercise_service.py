import logging
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from db_config.db_config import settings
import random

logger = logging.getLogger(__name__)


class ExerciseService:
    """Сервис для генерации упражнений по итальянскому"""

    def __init__(self):
        self.api_key = settings.openai.api_key
        self.enabled = settings.openai.enabled and bool(self.api_key)
        self.client = None

        if self.enabled:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("✓ Exercise service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize exercise service: {e}")
                self.enabled = False
        else:
            logger.info("Exercise service disabled")

    async def generate_gap_exercise(self, topic: str = "general", level: str = "beginner") -> Optional[Dict[str, Any]]:
        """
        Генерация упражнения на заполнение пропусков.
        """
        if not self.enabled:
            return None

        try:
            prompt = f"""Создай упражнение на заполнение пропусков для итальянского языка.

            Тема: {topic}
            Уровень: {level}

            Формат:
            ТЕКСТ_С_ПРОПУСКАМИ
            ---
            ПРАВИЛЬНЫЕ_ОТВЕТЫ (через запятую)
            ---
            ПЕРЕВОД_НА_РУССКИЙ

            Пример:
            Io ___ (essere) italiano. Mia sorella ___ (abitare) a Roma.
            ---
            sono, abita
            ---
            Я итальянец. Моя сестра живет в Риме."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()
            parts = result.split("---")

            if len(parts) >= 3:
                return {
                    "exercise": parts[0].strip(),
                    "answers": [ans.strip() for ans in parts[1].strip().split(",")],
                    "translation": parts[2].strip(),
                    "type": "gap_fill"
                }
            return None

        except Exception as e:
            logger.error(f"Error generating exercise: {e}")
            return None

    async def generate_quiz(self, topic: str = "vocabulary") -> Optional[Dict[str, Any]]:
        """
        Генерация викторины с множественным выбором.
        """
        if not self.enabled:
            return None

        try:
            prompt = f"""Создай викторину по итальянскому языку на тему '{topic}'.

            Формат:
            ВОПРОС
            A) вариант1
            B) вариант2  
            C) вариант3
            D) вариант4
            ---
            ПРАВИЛЬНЫЙ_ОТВЕТ (A/B/C/D)
            ---
            ОБЪЯСНЕНИЕ

            Пример:
            Как перевести 'яблоко' на итальянский?
            A) mela
            B) pera
            C) banana
            D) arancia
            ---
            A
            ---
            'Mela' - это яблоко на итальянском."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()
            parts = result.split("---")

            if len(parts) >= 3:
                return {
                    "question": parts[0].strip(),
                    "correct_answer": parts[1].strip(),
                    "explanation": parts[2].strip(),
                    "type": "quiz"
                }
            return None

        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return None