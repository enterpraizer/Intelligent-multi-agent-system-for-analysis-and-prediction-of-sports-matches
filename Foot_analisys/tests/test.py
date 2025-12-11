# llm_analysis_service.py
"""
Сервис для анализа футбольных матчей с помощью LLM
"""

import re
import logging
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMAnalysisService:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        """
        Инициализация сервиса LLM анализа

        Args:
            api_key: API ключ для OpenRouter
            base_url: Базовый URL API
        """
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = "tngtech/deepseek-r1t2-chimera:free"

        # Mock данные для команд (можно заменить на реальный team_stats_service)
        self.team_data = {
            "Arsenal": {
                "form": "WWWWD",
                "points": 13,
                "wins": 4, "draws": 1, "losses": 0,
                "goals_for_avg": 2.1, "goals_against_avg": 0.4,
                "home": "4-1-0", "away": "3-2-1"
            },
            "Tottenham": {
                "form": "LWDDW",
                "points": 8,
                "wins": 2, "draws": 2, "losses": 1,
                "goals_for_avg": 1.8, "goals_against_avg": 0.6,
                "home": "3-0-2", "away": "2-3-0"
            },
            "Man City": {
                "form": "WWLWW",
                "points": 12,
                "wins": 4, "draws": 0, "losses": 1,
                "goals_for_avg": 2.4, "goals_against_avg": 0.8,
                "home": "5-0-0", "away": "3-1-1"
            },
            "Liverpool": {
                "form": "DWWWD",
                "points": 11,
                "wins": 3, "draws": 2, "losses": 0,
                "goals_for_avg": 2.0, "goals_against_avg": 0.7,
                "home": "4-1-0", "away": "2-2-1"
            }
        }

    def create_match_analysis(self, home_team: str, away_team: str, detailed_prediction: dict) -> str:
        """
        Создает глубокий анализ матча с помощью LLM

        Args:
            home_team: Название домашней команды
            away_team: Название гостевой команды
            detailed_prediction: Детальный прогноз с статистикой

        Returns:
            str: Анализ матча от LLM
        """
        try:
            prompt = self._build_analysis_prompt(home_team, away_team, detailed_prediction)

            logger.info(f"Отправляем запрос к LLM для анализа {home_team} vs {away_team}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты - профессиональный футбольный аналитик. Твоя задача - делать анализ на основе ТОЛЬКО предоставленных данных.

ВАЖНЫЕ ПРАВИЛА:
1. НЕ используй Markdown разметку
2. НЕ выдумывай имена игроков, тренеров, тактики
3. НЕ придумывай статистику - используй только предоставленные цифры
4. Если данных мало - говори об этом прямо
5. Анализируй ТОЛЬКО на основе предоставленных чисел
6. Отвечай на ВСЕ 5 пунктов анализа
7. Используй эмодзи для наглядности

Отвечай на русском языке."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
            )

            analysis = response.choices[0].message.content

            # Проверяем, что ответ полный
            if self._is_response_complete(analysis):
                analysis = self._clean_formatting(analysis)
                logger.info(f"✅ LLM анализ успешно получен ({len(analysis)} символов)")
                return analysis
            else:
                logger.warning("❌ Ответ LLM обрезан, используем fallback")
                return self._get_fallback_analysis(home_team, away_team, detailed_prediction)

        except Exception as e:
            logger.error(f"Ошибка LLM анализа: {e}")
            return self._get_fallback_analysis(home_team, away_team, detailed_prediction)

    def _is_response_complete(self, text: str) -> bool:
        """Проверяет, что ответ полный (не обрезан)"""
        if not text:
            return False

        # Проверяем, что есть ответ на все ключевые темы
        required_topics = ['тактич', 'сильн', 'фактор', 'противостояни', 'рекомендац']
        found_topics = sum(1 for topic in required_topics if topic in text.lower())

        # Если найдено меньше 3 тем, считаем ответ неполным
        if found_topics < 3:
            return False

        # Проверяем, что текст заканчивается нормально (не обрывается)
        if text.strip().endswith(('.', '!', '?')):
            return True

        return len(text) > 200

    def _clean_formatting(self, text: str) -> str:
        """Очищает текст от Markdown форматирования"""
        if not text:
            return text

        # Удаляем Markdown синтаксис
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)

        # Удаляем заголовки Markdown
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

        # Удаляем разделители
        text = re.sub(r'-{3,}', '', text)
        text = re.sub(r'\*{3,}', '', text)
        text = re.sub(r'_{3,}', '', text)

        # Заменяем маркеры списков на эмодзи
        text = re.sub(r'^\s*[-*•]\s*', '• ', text, flags=re.MULTILINE)

        # Убираем лишние переносы строк
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text.strip()

    def _build_analysis_prompt(self, home_team: str, away_team: str, detailed_prediction: dict) -> str:
        """Строит промпт для анализа матча"""

        predictions = detailed_prediction.get('predictions', {})

        # БЕЗ ОКРУГЛЕНИЯ - используем оригинальные значения
        home_goals = predictions.get('Target_FTHG', 1.5)
        away_goals = predictions.get('Target_FTAG', 1.2)

        # Для счета используем математическое округление
        home_goals_int = round(home_goals)
        away_goals_int = round(away_goals)

        # Вероятности (такая же логика как в prediction_formatter)
        goal_diff = home_goals - away_goals
        if goal_diff > 0.5:
            home_prob = min(85, 50 + goal_diff * 15)
            away_prob = max(5, 20 - goal_diff * 10)
            result_text = f"Победа {home_team}"
        elif goal_diff < -0.5:
            away_prob = min(85, 50 - goal_diff * 15)
            home_prob = max(5, 20 + goal_diff * 10)
            result_text = f"Победа {away_team}"
        else:
            home_prob = 35
            away_prob = 35
            result_text = "Ничья"
        draw_prob = 100 - home_prob - away_prob

        # Форматируем данные БЕЗ ОКРУГЛЕНИЯ
        prediction_data = f"""
📊 ПРОГНОЗ И СТАТИСТИКА (РЕАЛЬНЫЕ ДАННЫЕ):

• Счет: {home_goals_int}:{away_goals_int}
• Вероятный результат: {result_text}
• Вероятности: {home_team} - {home_prob:.0f}%, Ничья - {draw_prob:.0f}%, {away_team} - {away_prob:.0f}%

• Голы: {home_goals:.3f} - {away_goals:.3f}
• Удары: {predictions.get('Target_HS', 0):.3f} - {predictions.get('Target_AS', 0):.3f}
• Удары в створ: {predictions.get('Target_HST', 0):.3f} - {predictions.get('Target_AST', 0):.3f}
• Угловые: {predictions.get('Target_HC', 0):.3f} - {predictions.get('Target_AC', 0):.3f}
• Фолы: {predictions.get('Target_HF', 0):.3f} - {predictions.get('Target_AF', 0):.3f}
• Желтые карточки: {predictions.get('Target_HY', 0):.3f} - {predictions.get('Target_AY', 0):.3f}
• Красные карточки: {predictions.get('Target_HR', 0):.3f} - {predictions.get('Target_AR', 0):.3f}
"""

        prompt = f"""
АНАЛИЗ МАТЧА: {home_team} vs {away_team}

{prediction_data}

🏃‍♂️ ДАННЫЕ О КОМАНДАХ:
{self._get_team_context(home_team)}
{self._get_team_context(away_team)}

🚨 ВАЖНЫЕ ОГРАНИЧЕНИЯ:
• НЕ выдумывай имена игроков, тренеров, тактики
• НЕ придумывай статистику - используй ТОЛЬКО цифры выше  
• Если данных мало - говори об этом прямо
• НЕ упоминай конкретных игроков - у тебя нет этих данных
• Анализируй ТОЛЬКО на основе предоставленных чисел

🎯 ЗАДАЧА (на основе РЕАЛЬНЫХ данных):
1. Тактический анализ - почему вероятен такой счет по статистике?
2. Сильные стороны - что показывают цифры формы и статистики?
3. Факторы влияния - какие статистические тенденции могут повлиять?
4. Ключевые аспекты - на что обратить внимание по данным?
5. Рекомендации - общие советы по просмотру матча

❌ ЗАПРЕЩЕНО: выдумывать имена, тактики, исторические факты
✅ РАЗРЕШЕНО: анализировать только предоставленные цифры
✅ ОБЯЗАТЕЛЬНО: закончи все 5 пунктов
"""
        return prompt

    def _get_team_context(self, team_name: str) -> str:
        """Получает контекстную информацию о команде"""
        try:
            team_info = self.team_data.get(team_name)

            if not team_info:
                return f"ℹ️ {team_name}: данные о команде недоступны\n\n"

            context = f"🔵 {team_name}:\n"
            context += f"• Форма: {team_info.get('form', 'N/A')}\n"
            context += f"• Очки в последних 5 матчах: {team_info.get('points', 0)}\n"
            context += f"• Победы/Ничьи/Поражения: {team_info.get('wins', 0)}/{team_info.get('draws', 0)}/{team_info.get('losses', 0)}\n"
            context += f"• Средние голы: {team_info.get('goals_for_avg', 0):.1f} забито, {team_info.get('goals_against_avg', 0):.1f} пропущено\n"

            # Домашняя/гостевая статистика
            home_record = team_info.get('home', 'N/A')
            away_record = team_info.get('away', 'N/A')

            context += f"• Дома: {home_record}\n"
            context += f"• В гостях: {away_record}\n"
            context += "• ⚠️ Используй только эти данные!\n\n"

            return context

        except Exception as e:
            logger.error(f"Ошибка получения контекста команды {team_name}: {e}")
            return f"ℹ️ {team_name}: ошибка загрузки данных\n\n"

    def _get_fallback_analysis(self, home_team: str, away_team: str, prediction: dict) -> str:
        """Fallback анализ если LLM недоступна"""
        predictions = prediction.get('predictions', {})
        home_goals = predictions.get('Target_FTHG', 1.5)
        away_goals = predictions.get('Target_FTAG', 1.2)

        return f"""
⚽ АНАЛИТИЧЕСКИЙ ОБЗОР МАТЧА

🏠 {home_team} против ✈️ {away_team}

📊 На основе статистического прогноза:

• Прогноз счета: {int(round(home_goals))}:{int(round(away_goals))}
• Статистические показатели указывают на определенные тенденции

🎯 КЛЮЧЕВЫЕ ВЫВОДЫ:
• Анализ основан на математических моделях
• Учитывается текущая форма команд
• Статистика реализации моментов

💡 РЕКОМЕНДАЦИИ:
Следите за основными статистическими показателями в матче

⚠️ Примечание: это базовый анализ на основе ограниченных данных
"""


def main():
    """Пример использования сервиса LLM анализа"""

    # Ваш API ключ
    API_KEY = "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"

    # Создаем экземпляр сервиса
    llm_service = LLMAnalysisService(api_key=API_KEY)

    # Тестовые данные для анализа
    test_prediction = {
        'predictions': {
            'Target_FTHG': 1.560,  # Голы домашней команды
            'Target_FTAG': 0.433,  # Голы гостевой команды
            'Target_HS': 5.589,  # Удары домашней
            'Target_AS': 3.997,  # Удары гостевой
            'Target_HST': 4.597,  # Удары в створ домашней
            'Target_AST': 2.345,  # Удары в створ гостевой
            'Target_HC': 2.148,  # Угловые домашней
            'Target_AC': 2.217,  # Угловые гостевой
            'Target_HF': 0.547,  # Фолы домашней
            'Target_AF': 2.387,  # Фолы гостевой
            'Target_HY': 0.341,  # Желтые домашней
            'Target_AY': 1.541,  # Желтые гостевой
            'Target_HR': 0.312,  # Красные домашней
            'Target_AR': 0.411,  # Красные гостевой
        }
    }

    print("🤖 ЗАПУСК ТЕСТА LLM АНАЛИЗА...")
    print("=" * 50)

    try:
        # Получаем анализ
        analysis = llm_service.create_match_analysis(
            home_team="Arsenal",
            away_team="Tottenham",
            detailed_prediction=test_prediction
        )

        print("✅ АНАЛИЗ УСПЕШНО ПОЛУЧЕН:")
        print("=" * 50)
        print(analysis)
        print("=" * 50)

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")


if __name__ == "__main__":
    main()