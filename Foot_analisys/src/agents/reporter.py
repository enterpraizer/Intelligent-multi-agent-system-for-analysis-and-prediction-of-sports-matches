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

    def _generate_template_report(self, home_team: str, away_team: str, predictions: Dict,
                                  features: Dict | None) -> str:
        """Генерация отчета по шаблону"""

        # Извлекаем предикты голов
        home_goals = float(round(predictions.get('Target_FTHG', 1.5), 1))
        away_goals = float(round(predictions.get('Target_FTAG', 1.2), 1))
        predicted_score = f"{int(round(home_goals))}:{int(round(away_goals))}"

        # Определяем результат и вероятности
        goal_diff = home_goals - away_goals
        if goal_diff > 0.5:
            result = "Победа хозяев"
            home_prob = min(85.0, 50.0 + goal_diff * 15.0)
            away_prob = max(5.0, 20.0 - goal_diff * 10.0)
        elif goal_diff < -0.5:
            result = "Победа гостей"
            away_prob = min(85.0, 50.0 - goal_diff * 15.0)
            home_prob = max(5.0, 20.0 + goal_diff * 10.0)
        else:
            result = "Ничья"
            home_prob = 35.0
            away_prob = 35.0

        draw_prob = max(0.0, 100.0 - home_prob - away_prob)

        # Другие статистики
        home_shots = float(round(predictions.get('Target_HS', 10), 1))
        away_shots = float(round(predictions.get('Target_AS', 8), 1))
        home_shots_target = float(round(predictions.get('Target_HST', 4), 1))
        away_shots_target = float(round(predictions.get('Target_AST', 3), 1))
        home_fouls = float(round(predictions.get('Target_HF', 12), 1))
        away_fouls = float(round(predictions.get('Target_AF', 11), 1))
        home_corners = float(round(predictions.get('Target_HC', 5), 1))
        away_corners = float(round(predictions.get('Target_AC', 4), 1))
        home_yellows = float(round(predictions.get('Target_HY', 2), 1))
        away_yellows = float(round(predictions.get('Target_AY', 2), 1))
        home_reds = float(round(predictions.get('Target_HR', 0), 1))
        away_reds = float(round(predictions.get('Target_AR', 0), 1))

        # Безопасная точность ударов
        home_shot_acc = home_shots_target / max(home_shots, 1.0) * 100.0
        away_shot_acc = away_shots_target / max(away_shots, 1.0) * 100.0

        header_line = "═" * 62

        report = f"""\
    {header_line}
    ПРОГНОЗ МАТЧАxxx: {home_team} vs {away_team}
    {header_line}

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
    Точность ударов           {home_shot_acc:<19.1f}% {away_shot_acc:<19.1f}%
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
            moments.append(f"• Ожидается результативный матч (прогноз: {total_goals:.1f} гола)")
        elif total_goals < 2:
            moments.append("• Ожидается низкая результативность")

        total_shots = home_shots + away_shots
        if total_shots > 20:
            moments.append(f"• Высокая активность в атаке (около {total_shots:.0f} ударов)")

        if home_shot_acc > 50:
            moments.append(f"• {home_team} будет точен в ударах ({home_shot_acc:.0f}% в створ)")

        if away_shot_acc > 50:
            moments.append(f"• {away_team} будет точен в ударах ({away_shot_acc:.0f}% в створ)")

        total_fouls = home_fouls + away_fouls
        if total_fouls > 22:
            moments.append(f"• Напряженный матч с большим количеством фолов ({total_fouls:.0f})")

        total_yellows = home_yellows + away_yellows
        if total_yellows > 4:
            moments.append(f"• Ожидается много карточек ({total_yellows:.0f} желтых)")

        if home_reds + away_reds >= 0.5:
            moments.append("• Есть риск удаления игрока")

        total_corners = home_corners + away_corners
        if total_corners > 10:
            moments.append(f"• Много угловых ударов ({total_corners:.0f})")

        # Доп. анализ по фичам, если есть
        if features:
            # Пример: если ты позже вернёшь winrate — всё не упадёт
            home_form = features.get('Home_WinRate_Last5')
            away_form = features.get('Away_WinRate_Last5')

            if home_form is not None:
                if home_form > 0.6:
                    moments.append(f"• {home_team} в хорошей форме ({home_form * 100:.0f}% побед в последних матчах)")
                elif home_form < 0.3:
                    moments.append(f"• {home_team} в слабой форме ({home_form * 100:.0f}% побед)")

            if away_form is not None:
                if away_form > 0.6:
                    moments.append(f"• {away_team} в хорошей форме ({away_form * 100:.0f}% побед)")
                elif away_form < 0.3:
                    moments.append(f"• {away_team} в слабой форме ({away_form * 100:.0f}% побед)")

            # Можно добавить простую интерпретацию Elo, если он есть
            diff_elo = features.get("Diff_Elo")
            if diff_elo is not None:
                if diff_elo > 50:
                    moments.append(f"• {home_team} заметно сильнее по рейтингу")
                elif diff_elo < -50:
                    moments.append(f"• {away_team} заметно сильнее по рейтингу")

        for moment in moments:
            report += moment + "\n"

        report += f"""
    💡 ЭКСПЕРТНЫЙ АНАЛИЗ
    {'─' * 62}
    """

        # Экспертный анализ
        if goal_diff > 1:
            report += f"{home_team} выглядят явными фаворитами. Ожидается уверенная победа со счетом {predicted_score}. "
        elif goal_diff < -1:
            report += f"{away_team} выглядят сильнее и имеют хорошие шансы на победу. Прогнозируемый счет {predicted_score} в пользу гостей. "
        else:
            report += f"Команды близки по уровню, прогнозируется упорная и равная борьба. "

        if total_goals > 3:
            report += "\n\nОжидается открытая и результативная игра с большим количеством моментов."
        elif total_goals < 2:
            report += "\n\nВероятна осторожная тактическая игра с небольшим количеством голов."

        if total_shots > 20:
            report += f" Обе команды будут часто угрожать воротам (около {total_shots:.0f} ударов)."

        report += f"""

    🎓 РЕКОМЕНДАЦИИ ДЛЯ ТРЕНЕРОВ
    {'─' * 62}
    Для тренера {home_team}:
    """

        if away_goals > 1.5:
            report += "• Уделить внимание организации обороны и компактности в штрафной.\n"
        if home_shot_acc < 40:
            report += "• Работать над качеством завершающей стадии атак и точностью ударов.\n"
        if away_fouls > 14:
            report += "• Использовать стандарты и быстрые фолы соперника в свою пользу.\n"

        report += f"\nДля тренера {away_team}:\n"

        if home_goals > 1.5:
            report += "• Сделать акцент на контратаках и свободных зонах за спинами защитников.\n"
        if home_shots > 12:
            report += "• Усилить прессинг в средней зоне, чтобы сократить число ударов хозяев.\n"
        if total_corners > 10:
            report += "• Особое внимание уделить игре при стандартах и подбору высоких игроков.\n"

        report += "\n" + header_line + "\n"

        return report

    def _generate_llm_report(self, home_team: str, away_team: str, predictions: Dict, features: Dict) -> str:
        """Генерация отчета через LLM"""
        # TODO: implement LLM generation
        return self._generate_template_report(home_team, away_team, predictions, features)