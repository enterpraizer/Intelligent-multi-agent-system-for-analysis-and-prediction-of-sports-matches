import re
import logging
from openai import OpenAI
from Foot_analisys.src.bot.services.team_stats_service import team_stats_service

logger = logging.getLogger(__name__)


class LLMAnalysisService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
        )
        self.model = "tngtech/deepseek-r1t2-chimera:free"

    def create_match_analysis(self, home_team: str, away_team: str, detailed_prediction: dict) -> str:
        """Создает глубокий анализ матча с помощью LLM"""
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

        # Проверяем, что текст заканчивается и не обрывается
        if text.strip().endswith(('.', '!', '?')):
            return True

        return len(text) > 200

    def _clean_formatting(self, text: str) -> str:
        """Очищает текст от Markdown форматирования"""
        if not text:
            return text

        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'-{3,}', '', text)
        text = re.sub(r'\*{3,}', '', text)
        text = re.sub(r'_{3,}', '', text)
        text = re.sub(r'^\s*[-*•]\s*', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text.strip()

    def _build_analysis_prompt(self, home_team: str, away_team: str, detailed_prediction: dict) -> str:
        """Строит промпт для анализа матча"""

        predictions = detailed_prediction.get('predictions', {})

        home_goals = predictions.get('Target_FTHG', 1.5)
        away_goals = predictions.get('Target_FTAG', 1.2)

        home_goals_int = round(home_goals)
        away_goals_int = round(away_goals)

        # Вероятности
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
            team_id = None
            for name, tid in team_stats_service.all_teams.items():
                if name.lower() == team_name.lower():
                    team_id = tid
                    break

            if not team_id:
                return f" {team_name}: ID команды не найден\n\n"

            stats = team_stats_service.get_team_stats(team_id)
            if not stats:
                return f"{team_name}: статистика недоступна\n\n"

            form = stats.get('form', {})
            home_away = stats.get('home_away', {})

            context = f" {team_name}:\n"

            context += f"• Форма: {form.get('form', 'N/A')}\n"
            context += f"• Очки в последних 5: {form.get('points', 0)}\n"
            context += f"• П/Н/П: {form.get('wins', 0)}/{form.get('draws', 0)}/{form.get('losses', 0)}\n"
            context += f"• Средние голы: {form.get('goals_for_avg', 0):.1f} забито, {form.get('goals_against_avg', 0):.1f} пропущено\n"

            home_stats = home_away.get('home', {})
            away_stats = home_away.get('away', {})

            home_matches = home_stats.get('W', 0) + home_stats.get('D', 0) + home_stats.get('L', 0)
            away_matches = away_stats.get('W', 0) + away_stats.get('D', 0) + away_stats.get('L', 0)

            if home_matches > 0:
                context += f"• Дома: {home_stats.get('W', 0)}-{home_stats.get('D', 0)}-{home_stats.get('L', 0)}\n"
            if away_matches > 0:
                context += f"• В гостях: {away_stats.get('W', 0)}-{away_stats.get('D', 0)}-{away_stats.get('L', 0)}\n"

            context += "• Используй только эти данные!\n\n"
            return context

        except Exception as e:
            logger.error(f"Ошибка получения контекста {team_name}: {e}")
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


llm_analysis_service = LLMAnalysisService()