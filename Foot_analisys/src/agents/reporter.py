"""
Агент-отчётчик: генерирует текстовый отчет на основе предиктов
"""
from typing import Dict
import logging
import os

logger = logging.getLogger(__name__)


class ReporterAgent:
    """Агент для генерации текстовых отчетов на основе предиктов"""

    def __init__(self, use_llm: bool = False, api_key: str = None):
        self.use_llm = use_llm
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        if self.use_llm and self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("LLM клиент инициализирован")
            except ImportError:
                logger.warning("OpenAI не установлен, используем шаблоны")
                self.use_llm = False
        else:
            logger.info("Используем шаблонную генерацию отчетов")
            self.use_llm = False

    def generate_report(self, home_team: str, away_team: str, predictions: Dict, features: Dict = None) -> str:
        """
        Генерирует отчет на основе предиктов

        Args:
            home_team: домашняя команда
            away_team: гостевая команда  
            predictions: словарь с предиктами от моделей (Target_FTHG, Target_FTAG и т.д.)
            features: опционально - фичи для дополнительного анализа
        """
        logger.info("Генерация отчета")

        if self.use_llm:
            return self._generate_llm_report(home_team, away_team, predictions, features)
        else:
            return self._generate_template_report(home_team, away_team, predictions, features)

    def _generate_template_report(self, home_team: str, away_team: str, predictions: Dict, features: Dict) -> str:
        """Генерация отчета по шаблону"""

        # Извлекаем предикты
        home_goals = round(predictions.get('Target_FTHG', 1.5), 1)
        away_goals = round(predictions.get('Target_FTAG', 1.2), 1)
        predicted_score = f"{int(round(home_goals))}:{int(round(away_goals))}"

        # Определяем результат
        goal_diff = home_goals - away_goals
        if goal_diff > 0.5:
            result = "Победа хозяев"
            home_prob = min(85, 50 + goal_diff * 15)
            away_prob = max(5, 20 - goal_diff * 10)
        elif goal_diff < -0.5:
            result = "Победа гостей"
            away_prob = min(85, 50 - goal_diff * 15)
            home_prob = max(5, 20 + goal_diff * 10)
        else:
            result = "Ничья"
            home_prob = 35
            away_prob = 35

        draw_prob = 100 - home_prob - away_prob

        # Другие статистики
        home_shots = round(predictions.get('Target_HS', 10), 1)
        away_shots = round(predictions.get('Target_AS', 8), 1)
        home_shots_target = round(predictions.get('Target_HST', 4), 1)
        away_shots_target = round(predictions.get('Target_AST', 3), 1)
        home_fouls = round(predictions.get('Target_HF', 12), 1)
        away_fouls = round(predictions.get('Target_AF', 11), 1)
        home_corners = round(predictions.get('Target_HC', 5), 1)
        away_corners = round(predictions.get('Target_AC', 4), 1)
        home_yellows = round(predictions.get('Target_HY', 2), 1)
        away_yellows = round(predictions.get('Target_AY', 2), 1)
        home_reds = round(predictions.get('Target_HR', 0), 1)
        away_reds = round(predictions.get('Target_AR', 0), 1)

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          ПРОГНОЗ МАТЧА: {home_team} vs {away_team}
╚══════════════════════════════════════════════════════════════╝

🎯 ОСНОВНОЙ ПРОГНОЗ
{'─' * 62}

Прогнозируемый счет: {predicted_score}
Ожидаемый результат: {result}

Вероятности исхода:
  • Победа {home_team}: {home_prob:.1f}%
  • Ничья: {draw_prob:.1f}%
  • Победа {away_team}: {away_prob:.1f}%


📊 ДЕТАЛЬНАЯ СТАТИСТИКА (ПРОГНОЗ)
{'─' * 62}

                          {home_team:<20} {away_team:<20}
Голы                      {home_goals:<20.1f} {away_goals:<20.1f}
Удары                     {home_shots:<20.1f} {away_shots:<20.1f}
Удары в створ             {home_shots_target:<20.1f} {away_shots_target:<20.1f}
Точность ударов           {home_shots_target / max(home_shots, 1) * 100:<19.1f}% {away_shots_target / max(away_shots, 1) * 100:<19.1f}%
Фолы                      {home_fouls:<20.1f} {away_fouls:<20.1f}
Угловые                   {home_corners:<20.1f} {away_corners:<20.1f}
Желтые карточки           {home_yellows:<20.1f} {away_yellows:<20.1f}
Красные карточки          {home_reds:<20.1f} {away_reds:<20.1f}


⚡ КЛЮЧЕВЫЕ МОМЕНТЫ
{'─' * 62}
"""

        # Анализ ключевых моментов
        moments = []

        total_goals = home_goals + away_goals
        if total_goals > 3:
            moments.append(f"• Ожидается результативный матч (прогноз: {total_goals:.1f} голов)")
        elif total_goals < 2:
            moments.append("• Ожидается низкая результативность")

        total_shots = home_shots + away_shots
        if total_shots > 20:
            moments.append(f"• Высокая активность в атаке ({total_shots:.0f} ударов)")

        if home_shots_target / max(home_shots, 1) > 0.5:
            moments.append(
                f"• {home_team} будет точен в ударах ({home_shots_target / max(home_shots, 1) * 100:.0f}% точность)")

        if away_shots_target / max(away_shots, 1) > 0.5:
            moments.append(
                f"• {away_team} будет точен в ударах ({away_shots_target / max(away_shots, 1) * 100:.0f}% точность)")

        total_fouls = home_fouls + away_fouls
        if total_fouls > 22:
            moments.append(f"• Напряженный матч с большим количеством фолов ({total_fouls:.0f})")

        total_yellows = home_yellows + away_yellows
        if total_yellows > 4:
            moments.append(f"• Ожидается много карточек ({total_yellows:.0f} желтых)")

        if home_reds + away_reds >= 0.5:
            moments.append("• Высокая вероятность удаления игрока")

        total_corners = home_corners + away_corners
        if total_corners > 10:
            moments.append(f"• Много угловых ударов ({total_corners:.0f})")

        # Добавляем анализ по фичам, если есть
        if features:
            home_form = features.get('Home_WinRate_Last5', 0)
            away_form = features.get('Away_WinRate_Last5', 0)

            if home_form > 0.6:
                moments.append(f"• {home_team} в отличной форме ({home_form * 100:.0f}% побед)")
            elif home_form < 0.3:
                moments.append(f"• {home_team} в кризисе ({home_form * 100:.0f}% побед)")

            if away_form > 0.6:
                moments.append(f"• {away_team} в отличной форме ({away_form * 100:.0f}% побед)")
            elif away_form < 0.3:
                moments.append(f"• {away_team} в кризисе ({away_form * 100:.0f}% побед)")

        for moment in moments:
            report += moment + "\n"

        report += f"""

💡 ЭКСПЕРТНЫЙ АНАЛИЗ
{'─' * 62}
"""

        # Экспертный анализ
        if goal_diff > 1:
            report += f"{home_team} являются явными фаворитами этого матча. "
            report += f"Прогнозируется уверенная победа со счетом {predicted_score}. "
        elif goal_diff < -1:
            report += f"{away_team} выглядят сильнее и способны одержать победу. "
            report += f"Прогнозируемый счет {predicted_score} в пользу гостей. "
        else:
            report += f"Команды примерно равны по силе. Прогнозируется упорная борьба. "

        if total_goals > 3:
            report += f"\n\nОжидается открытая и результативная игра. Обе команды будут активно атаковать. "
        elif total_goals < 2:
            report += f"\n\nПрогнозируется тактическая борьба с низкой результативностью. "

        if total_shots > 20:
            report += f"Обе команды создадут много моментов ({total_shots:.0f} ударов). "

        report += f"""


🎓 РЕКОМЕНДАЦИИ ДЛЯ ТРЕНЕРОВ
{'─' * 62}

Для тренера {home_team}:
"""

        if away_goals > 1.5:
            report += f"• Оборона соперника нестабильна - активизировать атаку\n"
        if home_shots_target / max(home_shots, 1) < 0.4:
            report += f"• Улучшить точность ударов и реализацию моментов\n"
        if away_fouls > 14:
            report += f"• Соперник склонен к грубой игре - использовать технику и стандарты\n"

        report += f"\nДля тренера {away_team}:\n"

        if home_goals > 1.5:
            report += f"• Оборона хозяев уязвима - делать ставку на контратаки\n"
        if home_shots > 12:
            report += f"• Хозяева активны в атаке - усилить оборону\n"
        if total_corners > 10:
            report += f"• Ожидается много стандартов - отработать розыгрыши угловых\n"

        report += "\n" + "═" * 62 + "\n"

        return report

    def _generate_llm_report(self, home_team: str, away_team: str, predictions: Dict, features: Dict) -> str:
        """Генерация отчета через LLM"""
        # TODO: implement LLM generation
        return self._generate_template_report(home_team, away_team, predictions, features)