"""
Координатор: управляет потоком данных между агентами
Analyst -> Predictor -> Reporter
"""
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Foot_analisys.src.agents.analyst import AnalystAgent
from Foot_analisys.src.agents.predictor import PredictorAgent
from Foot_analisys.src.agents.reporter import ReporterAgent
from typing import Dict

logger = logging.getLogger(__name__)


class MatchCoordinator:
    """
    Координатор агентов:
    1. Analyst строит фичи из исторических данных
    2. Predictor делает предикт на основе фичей
    3. Reporter генерирует текстовый отчет
    """

    def __init__(self,
                 use_llm: bool = False):

        logger.info("Инициализация координатора")

        self.analyst = AnalystAgent()
        self.predictor = PredictorAgent()
        self.reporter = ReporterAgent(use_llm=use_llm)

        self.initialized = False

    def initialize(self) -> bool:
        """Загрузка данных и моделей"""
        logger.info("Загрузка данных...")

        if not self.analyst.load_data():
            logger.error("Ошибка загрузки данных")
            return False

        if len(self.predictor.predictor.models) == 0:
            logger.error("Модели не загружены")
            return False

        self.initialized = True
        logger.info("✓ Координатор готов к работе")
        return True

    def predict_match(self, home_team: str, away_team: str) -> Dict:
        """
        Полный цикл прогноза:
        Analyst строит фичи -> Predictor делает предикт -> Reporter генерирует отчет
        """
        if not self.initialized:
            if not self.initialize():
                return {
                    'success': False,
                    'error': 'Не удалось инициализировать систему'
                }

        logger.info(f"{'='*70}")
        logger.info(f"Прогноз матча: {home_team} vs {away_team}")
        logger.info(f"{'='*70}")

        # ШАГ 1: Analyst строит фичи
        logger.info("Шаг 1/3: Analyst строит фичи из исторических данных...")

        analysis_result = self.analyst.analyze_match(home_team, away_team)

        if not analysis_result.get('success'):
            return {
                'success': False,
                'error': analysis_result.get('error', 'Ошибка анализа')
            }

        features_df = analysis_result['features']
        features_dict = analysis_result['features_dict']

        logger.info(f"✓ Analyst построил {len(features_dict)} фичей")

        # ШАГ 2: Predictor делает предикт
        logger.info("Шаг 2/3: Predictor делает предсказания...")

        prediction_result = self.predictor.predict(features_df)

        if not prediction_result.get('success'):
            return {
                'success': False,
                'error': prediction_result.get('error', 'Ошибка предсказания')
            }

        predictions = prediction_result['predictions']

        logger.info(f"✓ Predictor вернул {len(predictions)} предсказаний")

        # ШАГ 3: Reporter генерирует отчет
        logger.info("Шаг 3/3: Reporter генерирует текстовый отчет...")

        report = self.reporter.generate_report(
            home_team=home_team,
            away_team=away_team,
            predictions=predictions,
            features=features_dict
        )

        logger.info("✓ Reporter сгенерировал отчет")
        logger.info(f"{'='*70}")
        logger.info("Прогноз завершен успешно")
        logger.info(f"{'='*70}")

        return {
            'success': True,
            'home_team': home_team,
            'away_team': away_team,
            'features': features_dict,
            'predictions': predictions,
            'report': report
        }

    def quick_predict(self, home_team: str, away_team: str) -> str:
        """Быстрый прогноз - только основные данные"""
        result = self.predict_match(home_team, away_team)

        if not result['success']:
            return f"❌ Ошибка: {result.get('error')}"

        p = result['predictions']
        home_goals = round(p.get('Target_FTHG', 1.5), 1)
        away_goals = round(p.get('Target_FTAG', 1.2), 1)
        score = f"{int(round(home_goals))}:{int(round(away_goals))}"

        # Вероятности
        goal_diff = home_goals - away_goals
        if goal_diff > 0.5:
            home_prob = min(85, 50 + goal_diff * 15)
            away_prob = max(5, 20 - goal_diff * 10)
        elif goal_diff < -0.5:
            away_prob = min(85, 50 - goal_diff * 15)
            home_prob = max(5, 20 + goal_diff * 10)
        else:
            home_prob = 35
            away_prob = 35

        draw_prob = 100 - home_prob - away_prob

        return f"""
🎯 БЫСТРЫЙ ПРОГНОЗ: {home_team} vs {away_team}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Прогноз счета: {score}

Вероятности:
  🏠 Победа хозяев: {home_prob:.1f}%
  🤝 Ничья: {draw_prob:.1f}%
  ✈️  Победа гостей: {away_prob:.1f}%
"""

    def get_team_list(self, league_idx: int = -1) -> list:
        """Получение списка всех команд из данных"""
        if not self.initialized:
            self.initialize()

        if self.analyst.df_matches is None:
            return []

        if league_idx == -1:
            teams = set(self.analyst.df_matches['HomeTeam'].unique()) | \
                    set(self.analyst.df_matches['AwayTeam'].unique())
            teams = [t for t in teams if isinstance(t, str) and t.strip().lower() != "nan"]

            return sorted(list(teams))
        else:
            league_teams = self.analyst.df_matches[self.analyst.df_matches['league'] == self.analyst.league[league_idx]]


            teams = set(league_teams['HomeTeam'].unique()) | \
                    set(league_teams['AwayTeam'].unique())
            teams = [t for t in teams if isinstance(t, str) and t.strip().lower() != "nan"]

            return sorted(list(teams))


    def get_league_list(self) -> list:
        if not self.initialized:
            self.initialize()

        if self.analyst.df_matches is None:
            return []

        leagues = self.analyst.league

        return leagues

    def compare_teams(self, team1: str, team2: str) -> str:
        """Сравнение статистики двух команд"""
        if not self.initialized:
            self.initialize()

        # Строим фичи для каждой команды как если бы они играли друг с другом
        result1 = self.analyst.analyze_match(team1, team2)
        result2 = self.analyst.analyze_match(team2, team1)

        if not result1.get('success') or not result2.get('success'):
            return "❌ Ошибка получения статистики команд"

        f1 = result1['features_dict']
        f2 = result2['features_dict']

        return f"""
📊 СРАВНЕНИЕ КОМАНД
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{team1} vs {team2}

Показатель                    {team1:<15} {team2:<15}
{'─' * 60}
Средние голы (5 матчей)       {f1.get('Home_GoalsScored_Last5', 0):<15.2f} {f2.get('Home_GoalsScored_Last5', 0):<15.2f}
Пропускает голов              {f1.get('Home_GoalsConceded_Last5', 0):<15.2f} {f2.get('Home_GoalsConceded_Last5', 0):<15.2f}
Процент побед                 {f1.get('Home_WinRate_Last5', 0)*100:<14.1f}% {f2.get('Home_WinRate_Last5', 0)*100:<14.1f}%
Разница голов                 {f1.get('Home_GoalDiff_Last5', 0):<15.2f} {f2.get('Home_GoalDiff_Last5', 0):<15.2f}
Средние удары                 {f1.get('Home_AvgHS_Last5', 0):<15.2f} {f2.get('Home_AvgHS_Last5', 0):<15.2f}
Удары в створ                 {f1.get('Home_AvgHST_Last5', 0):<15.2f} {f2.get('Home_AvgHST_Last5', 0):<15.2f}
"""

    def get_status(self) -> Dict:
        """Статус системы"""
        return {
            'initialized': self.initialized,
            'data_loaded': self.analyst.df_matches is not None,
            'models_loaded': len(self.predictor.predictor.models),
            'llm_enabled': self.reporter.use_llm,
        }

    def get_match_features(self, home_team: str, away_team: str) -> Dict:
        """Получить только фичи для матча (для отладки)"""
        if not self.initialized:
            self.initialize()

        result = self.analyst.analyze_match(home_team, away_team)
        return result


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Создание координатора
    coordinator = MatchCoordinator()

    if coordinator.initialize():
        print("✅ Система инициализирована\n")

        teams = coordinator.get_team_list()
        print(f"Команд в базе: {len(teams)}")
        print(f"Примеры: {', '.join(teams[:5])}\n")

        if len(teams) >= 2:
            print(f"Прогноз: {teams[0]} vs {teams[1]}\n")
            result = coordinator.predict_match(teams[0], teams[1])

            if result['success']:
                print(result['report'])
            else:
                print(f"Ошибка: {result['error']}")
    else:
        print("❌ Ошибка инициализации")