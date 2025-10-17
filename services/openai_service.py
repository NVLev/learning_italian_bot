import logging
from typing import Optional
from openai import AsyncOpenAI
from db_config.db_config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Сервис для взаимодействия с OpenAI API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация сервиса OpenAI.
        """
        self.api_key = settings.openai.api_key
        self.client = None
        self.enabled = settings.openai.enabled and bool(self.api_key)

        if self.api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                self.enabled = True
                logger.info("Сервис OpenAI инициализирован")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать OpenAI: {e}")
                self.enabled = False
        else:
            logger.warning("Сервис OpenAI отключен - нет API ключа или сервис выключен ")

    async def check_api_key(self) -> bool:
        """
        Проверка актуальности ключа API key простым запросом.

        Returns:
            bool: True если API ключ работает, False в противном случае
        """
        if not self.enabled or not self.client:
            return False

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Say 'test' in Italian"}],
                max_tokens=5
            )
            logger.info("ключ OpenAI API действует")
            return True
        except Exception as e:
            logger.error(f"Тест ключа OpenAI API не прошел: {e}")
            self.enabled = False
            return False

    async def explain_word(
            self,
            italian_word: str,
            russian_translation: str = ""
    ) -> Optional[str]:
        """
        Генерация объяснения для итальянского слова.

        Args:
            italian_word: слово для объяснения
            russian_translation: перевод на русский

        Returns:
            отформатированное объяснение или None
        """
        if not self.enabled:
            logger.warning("OpenAI service is disabled")
            return None

        try:
            # ИСПРАВЛЕНО: Упрощенный промпт без перевода
            prompt = f"""Ты - преподаватель итальянского языка для русскоговорящих студентов.

        Слово: {italian_word}

        Дай краткое объяснение (максимум 250 слов):
        1. Перевод на русский
        2. 2-3 примера использования в итальянских предложениях с переводом
        3. 1-2 синонима (если есть)
        4. Короткую мнемоническую подсказку для запоминания

        Формат ответа должен быть понятным и структурированным."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "Ты - опытный преподаватель итальянского языка для русских студентов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )

            explanation = response.choices[0].message.content
            logger.info(f"Generated explanation for word: {italian_word}")

            return explanation

        except Exception as e:
            logger.error(f"Ошибка генерации объяснения: {e}")
            return None

    async def generate_example_sentence(
            self,
            italian_word: str
    ) -> Optional[str]:
        """
        Генерация примера простого предложения с данным словом.

        Args:
            italian_word: итальянское слово

        Returns:
            Предложение на итальянском языке или None
        """
        if not self.enabled:
            return None

        try:
            prompt = f"Придумай одно простое итальянское предложение со словом '{italian_word}' и переведи его на русский. Формат: 'Итальянское предложение | Русский перевод'"

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating sentence: {e}")
            return None


# Global instance (lazy initialization)
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """
    Получение или создание экземпляра сервиса OpenAI.

    Returns:
        Экземпляр OpenAIService
    """
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service


async def is_openai_available() -> bool:
    """
    Проверка доступности сервиса OpenAI.

    Returns:
        bool: True если сервис доступен и работает
    """
    service = get_openai_service()
    if not service.enabled:
        return False
    return await service.check_api_key()