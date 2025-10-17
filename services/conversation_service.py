import logging
from typing import Optional, Any, Coroutine
from openai import AsyncOpenAI
from db_config.db_config import settings

logger = logging.getLogger(__name__)


class ConversationService:
    """Сервис для диалоговой практики итальянского языка"""

    def __init__(self):
        self.api_key = settings.openai.api_key
        self.enabled = settings.openai.enabled and bool(self.api_key)
        self.client = None

        if self.enabled:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("✓ Conversation service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize conversation service: {e}")
                self.enabled = False
        else:
            logger.info("Conversation service disabled")

    async def start_conversation(self, user_level: str = "beginner") -> tuple[str, str]:
        """
        Начало диалога на итальянском.

        Args:
            user_level: Уровень пользователя (beginner, intermediate, advanced)

        Returns:
            tuple: (итальянская фраза, русский перевод)
        """
        if not self.enabled:
            return "Сервис диалогов временно недоступен", ""

        try:
            prompt = f"""Ты - терпеливый преподаватель итальянского. Начни простой диалог на итальянском для уровня {user_level}.

            Верни ТОЛЬКО в формате:
            ИТАЛЬЯНСКАЯ_ФРАЗА|РУССКИЙ_ПЕРЕВОД

            Пример: Ciao, come stai?|Привет, как дела?"""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()
            if "|" in result:
                italian, russian = result.split("|", 1)
                return italian.strip(), russian.strip()
            else:
                return result, ""

        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return "Извините, произошла ошибка", ""

    async def continue_conversation(self, user_message: str, conversation_history: list) -> tuple[str, str, list] | \
                                                                                            tuple[str, str, list, str]:
        """
        Продолжение диалога на основе ответа пользователя.

        Args:
            user_message: Сообщение пользователя на итальянском
            conversation_history: История диалога

        Returns:
            tuple: (итальянский ответ, русский перевод, обновленная история)
        """
        if not self.enabled:
            return "Сервис диалогов временно недоступен", "", conversation_history

        try:
            # Добавляем сообщение пользователя в историю
            conversation_history.append({"role": "user", "content": user_message})

            system_prompt = """Ты - терпеливый преподаватель итальянского. Веди диалог с учеником:
            1. Ответь на его сообщение естественно на итальянском
            2. Если в ответе есть ошибки - мягко поправь их
            3. Дай русский перевод своего ответа

            Формат ответа:
            ИТАЛЬЯНСКИЙ_ОТВЕТ|РУССКИЙ_ПЕРЕВОД|[КОММЕНТАРИЙ_ОБ_ОШИБКАХ]"""

            messages = [
                           {"role": "system", "content": system_prompt}
                       ] + conversation_history[-6:]  # Берем последние 6 сообщений для контекста

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()
            parts = result.split("|", 2)

            italian_response = parts[0].strip()
            russian_translation = parts[1].strip() if len(parts) > 1 else ""
            correction = parts[2].strip() if len(parts) > 2 else ""

            # Добавляем ответ ассистента в историю
            conversation_history.append({"role": "assistant", "content": italian_response})

            return italian_response, russian_translation, conversation_history, correction

        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return "Извините, произошла ошибка", "", conversation_history, ""