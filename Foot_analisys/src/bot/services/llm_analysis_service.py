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
        # self.model = "deepseek/deepseek-chat-v3-0324:free"
        # self.model = "openai/gpt-oss-20b:free"
        self.model = "openrouter/sherlock-dash-alpha"

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
                        "content": """Ты - профессиональный футбольный аналитик. Твоя задача - делать глубокий анализ предстоящих матчей.

ВАЖНЫЕ ПРАВИЛА:
1. НЕ используй Markdown (**жирный**, *курсив*)
2. Пиши ТОЛЬКО обычный текст
3. ОБЯЗАТЕЛЬНО ответь на ВСЕ 5 вопросов:
   - Тактический анализ
   - Сильные стороны команд  
   - Факторы влияния
   - Ключевые противостояния
   - Рекомендации зрителям
4. Минимум 300 слов, максимум 500 слов
5. ЗАКОНЧИ полным ответом, не обрывай
6. Используй эмодзи для наглядности

Отвечай на русском языке."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,  # Увеличиваем лимит
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

        return len(text) > 200  # Минимальная длина ответа

    def _clean_formatting(self, text: str) -> str:
        """Очищает текст от Markdown форматирования"""
        if not text:
            return text

        # Удаляем Markdown синтаксис
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **жирный**
        text = re.sub(r'\*(.*?)\*', r'\1', text)  # *курсив*
        text = re.sub(r'_(.*?)_', r'\1', text)  # _подчеркивание_
        text = re.sub(r'`(.*?)`', r'\1', text)  # `код`

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

        # Обрезаем обрывки
        text = self._fix_truncated_text(text)

        return text.strip()

    def _fix_truncated_text(self, text: str) -> str:
        """Исправляет обрыв текста"""
        # Если текст обрывается на полуслове, обрезаем до последнего предложения
        sentences = re.split(r'[.!?]', text)
        if len(sentences) > 1:
            # Берем все кроме последнего (возможно обрезанного) предложения
            complete_sentences = sentences[:-1]
            return '.'.join(complete_sentences) + '.'
        return text

    def _build_analysis_prompt(self, home_team: str, away_team: str, detailed_prediction: dict) -> str:
        """Строит промпт для анализа матча"""

        predictions = detailed_prediction.get('predictions', {})

        # Базовые вероятности
        home_goals = predictions.get('Target_FTHG', 1.5)
        away_goals = predictions.get('Target_FTAG', 1.2)

        # Рассчитываем вероятности исхода
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

        prompt = f"""
АНАЛИЗ ФУТБОЛЬНОГО МАТЧА

КОМАНДЫ: {home_team} 🆚 {away_team}

📊 ПРОГНОЗ:
• Счет: {int(round(home_goals))}:{int(round(away_goals))}
• Вероятный результат: {result_text}
• Вероятности: {home_team} - {home_prob}%, Ничья - {draw_prob}%, {away_team} - {away_prob}%

📈 СТАТИСТИКА:
• Голы: {home_goals:.1f} - {away_goals:.1f}
• Удары: {predictions.get('Target_HS', 10):.1f} - {predictions.get('Target_AS', 8):.1f}
• Удары в створ: {predictions.get('Target_HST', 4):.1f} - {predictions.get('Target_AST', 3):.1f}
• Угловые: {predictions.get('Target_HC', 5):.1f} - {predictions.get('Target_AC', 4):.1f}
• Фолы: {predictions.get('Target_HF', 12):.1f} - {predictions.get('Target_AF', 11):.1f}

🏃‍♂️ ФОРМА КОМАНД:
{self._get_team_context(home_team)}
{self._get_team_context(away_team)}

🎯 ЗАДАНИЕ:
Сделай полный анализ матча. ОБЯЗАТЕЛЬНО ответь на ВСЕ пункты:

1. ТАКТИЧЕСКИЙ АНАЛИЗ - Почему вероятен именно такой счет? Какие тактические схемы будут использовать команды?

2. СИЛЬНЫЕ СТОРОНЫ - На какие сильные качества могут опереться обе команды?

3. ФАКТОРЫ ВЛИЯНИЯ - Что может кардинально изменить прогноз? Травмы, мотивация, тактические сюрпризы?

4. КЛЮЧЕВЫЕ ПРОТИВОСТОЯНИЯ - В каких позициях решится исход матча? Ключевые игроки.

5. РЕКОМЕНДАЦИИ ЗРИТЕЛЯМ - На что стоит обратить внимание во время матча?

❌ НЕ ИСПОЛЬЗУЙ Markdown разметку!
✅ ПИШИ обычным текстом с абзацами
✅ ИСПОЛЬЗУЙ эмодзи для наглядности
✅ ОБЯЗАТЕЛЬНО закончи все 5 пунктов
✅ МИНИМУМ 300 слов

Начинай анализ прямо с первого пункта, без вступления.
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
                return f"ℹ️ {team_name}: данные недоступны\n\n"

            stats = team_stats_service.get_team_stats(team_id)
            if not stats:
                return f"ℹ️ {team_name}: статистика недоступна\n\n"

            form = stats['form']
            home_away = stats['home_away']
            series = stats['series']

            # Форматируем информацию о команде
            context = f"🔵 {team_name}:\n"
            context += f"• Форма: {form.get('form', 'N/A')}\n"
            context += f"• Очки в последних 5 матчах: {form.get('points', 0)}\n"
            context += f"• Победы/Ничьи/Поражения: {form.get('wins', 0)}/{form.get('draws', 0)}/{form.get('losses', 0)}\n"
            context += f"• Средние голы: {form.get('goals_for_avg', 0):.1f} забито, {form.get('goals_against_avg', 0):.1f} пропущено\n"

            # Добавляем информацию о сериях
            if series.get('unbeaten', 0) > 0:
                context += f"• Без поражений: {series['unbeaten']} матчей\n"
            if series.get('win_streak', 0) > 0:
                context += f"• Победная серия: {series['win_streak']} матчей\n"

            context += "\n"
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

🎯 ТАКТИЧЕСКИЙ АНАЛИЗ
Прогноз счета {int(round(home_goals))}:{int(round(away_goals))} основан на текущей форме команд и статистических показателях. Ожидается напряженная борьба в центре поля.

💪 СИЛЬНЫЕ СТОРОНЫ
• {home_team}: Опорная зона и организация атак
• {away_team}: Контратаки и оборонительная дисциплина

📊 ФАКТОРЫ ВЛИЯНИЯ
• Составы команд и возможные травмы ключевых игроков
• Тактические решения главных тренеров
• Психологический фактор и мотивация

🔑 КЛЮЧЕВЫЕ ПРОТИВОСТОЯНИЯ
• Борьба в центральной зоне midfield
• Действия крайних защитников и вингеров
• Эффективность нападающих в завершении атак

👀 РЕКОМЕНДАЦИИ ЗРИТЕЛЯМ
Следите за первыми 15 минутами матча - они покажут тактические установки команд. Обратите внимание на борьбу в центре поля и эффективность стандартных положений.

💡 Этот анализ создан на основе статистических данных и текущей формы команд.
"""

    def _get_result_tendency(self, prediction: dict) -> str:
        """Анализ тенденции результата"""
        predictions = prediction.get('predictions', {})
        home_goals = predictions.get('Target_FTHG', 1.5)
        away_goals = predictions.get('Target_FTAG', 1.2)

        if home_goals > away_goals + 0.5:
            return "потенциальную победу домашней команды"
        elif away_goals > home_goals + 0.5:
            return "потенциальную победу гостевой команды"
        else:
            return "открытый и равный матч"


# Глобальный экземпляр сервиса
llm_analysis_service = LLMAnalysisService()