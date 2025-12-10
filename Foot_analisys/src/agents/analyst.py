"""
Агент-аналитик: строит фичи для предсказания на основе исторических данных
"""
import pandas as pd
import numpy as np
from typing import Dict
import logging
from pathlib import Path
logger = logging.getLogger(__name__)


class AnalystAgent:
    """Агент для построения признаков (фичей) из исторических данных матчей"""

    def __init__(self):
        PROJECT_ROOT = Path(__file__).resolve().parents[2]

        # Формируем путь к файлу относительно корня проекта
        self.data_path: str = str(PROJECT_ROOT / "data" / "processed" / "all_matches.csv")
        self.df_matches = None
        self.league = ['Bundes Ligue','EPL','Ligue1','LL','Serie A']

    def load_data(self) -> bool:
        """Загрузка исторических данных"""
        try:
            self.df_matches = pd.read_csv(self.data_path, parse_dates=['Date'], dayfirst=True)
            logger.info(f"Данные загружены: {len(self.df_matches)} матчей")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return False

    def build_features_for_match(self, home_team: str, away_team: str, last_n: int = 10) -> pd.DataFrame:
        """
        Строит фичи для матча на основе последних N матчей каждой команды и H2H
        Применяет веса: H2H = 0.7, Home/Away = 0.3 для голов и ударов
        Возвращает DataFrame с одной строкой взвешенных фичей
        """
        if self.df_matches is None:
            logger.error("Данные не загружены")
            return pd.DataFrame()

        logger.info(f"Строю фичи для {home_team} vs {away_team}")

        # Фичи для домашней команды
        home_features = self._get_team_features(home_team, last_n, prefix='Home')

        # Фичи для гостевой команды
        away_features = self._get_team_features(away_team, last_n, prefix='Away')

        # H2H фичи
        h2h_features = self._get_h2h_features(home_team, away_team, last_n)

        # Объединяем все фичи
        features = {}
        features.update(home_features)
        features.update(away_features)
        features.update(h2h_features)

        # Применяем веса только к голам и ударам
        weighted_stats = ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST']
        weighted_features = {}
        for col, val in features.items():
            if any(col.endswith(f"{stat}_avg") for stat in weighted_stats):
                if col.startswith("H2H_"):
                    weighted_features[col] = val * 0.7
                elif col.startswith("Home_") or col.startswith("Away_"):
                    weighted_features[col] = val * 0.3
            else:
                weighted_features[col] = val  # оставляем без изменений

        logger.info(f"Построено взвешенных фичей: {len(weighted_features)}")

        return pd.DataFrame([weighted_features])

    def _get_team_features(self, team: str, last_n: int, prefix: str) -> Dict:
        """Вычисляет средние показатели команды за последние N матчей"""
        # Находим последние N матчей команды (дома и в гостях)
        print(team)
        last_matches = self.df_matches[
            (self.df_matches['HomeTeam'] == team) | (self.df_matches['AwayTeam'] == team)
            ].sort_values(by='Date', ascending=False).head(last_n)

        if len(last_matches) == 0:
            logger.warning(f"Нет данных для команды {team}")
            return self._get_default_features(prefix, last_n)

        features = {}

        stats_to_calc = ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']

        for stat in stats_to_calc:
            values = []

            for _, row in last_matches.iterrows():
                if row['HomeTeam'] == team:
                    # Команда играла дома
                    values.append(row.get(stat, 0))
                elif row['AwayTeam'] == team:
                    # Команда играла в гостях
                    # Заменяем H на A и наоборот, чтобы брать "свою" статистику
                    if stat.startswith('H'):
                        alt_stat = 'A' + stat[1:]  # например, HS → AS
                    elif stat.startswith('A'):
                        alt_stat = 'H' + stat[1:]  # например, AS → HS
                    elif stat == 'FTHG':
                        alt_stat = 'FTAG'
                    elif stat == 'FTAG':
                        alt_stat = 'FTHG'
                    else:
                        alt_stat = stat
                    values.append(row.get(alt_stat, 0))

            # Среднее значение
            avg_val = np.mean(values) if values else 0.0
            features[f'{prefix}_{stat}_avg'] = round(avg_val, 2)

        """# Дополнительные метрики
        # Форма команды (процент побед)
        wins = sum(1 for _, row in last_matches.iterrows()
                   if (row['HomeTeam'] == team and row.get('FTHG', 0) > row.get('FTAG', 0)) or
                   (row['AwayTeam'] == team and row.get('FTAG', 0) > row.get('FTHG', 0)))

        features[f'{prefix}_WinRate_Last{last_n}'] = round(wins / len(last_matches), 3)

        # Разница забитых и пропущенных голов
        goals_scored = sum(row.get('FTHG' if row['HomeTeam'] == team else 'FTAG', 0)
                           for _, row in last_matches.iterrows())
        goals_conceded = sum(row.get('FTAG' if row['HomeTeam'] == team else 'FTHG', 0)
                             for _, row in last_matches.iterrows())

        features[f'{prefix}_GoalDiff_Last{last_n}'] = round(goals_scored - goals_conceded, 2)
        features[f'{prefix}_GoalsScored_Last{last_n}'] = round(goals_scored, 2)
        features[f'{prefix}_GoalsConceded_Last{last_n}'] = round(goals_conceded, 2)
"""
        return features

    def _get_h2h_features(self, home_team: str, away_team: str, last_n: int) -> Dict:
        """Вычисляет статистику личных встреч команд"""
        h2h_matches = self.df_matches[
            ((self.df_matches['HomeTeam'] == home_team) & (self.df_matches['AwayTeam'] == away_team)) |
            ((self.df_matches['HomeTeam'] == away_team) & (self.df_matches['AwayTeam'] == home_team))
            ].sort_values(by='Date', ascending=False)

        features = {}

        """if len(h2h_matches) == 0:
            logger.warning(f"Нет H2H данных для {home_team} vs {away_team}")
            features[f'H2H_MatchesPlayed'] = 0
            features[f'H2H_HomeWins'] = 0
            features[f'H2H_AwayWins'] = 0
            features[f'H2H_Draws'] = 0
            features[f'H2H_AvgGoals'] = 0.0
            features[f'H2H_AvgHomeGoals'] = 0.0
            features[f'H2H_AvgAwayGoals'] = 0.0
            return features

        # Количество матчей
        features[f'H2H_MatchesPlayed'] = len(h2h_matches)

        # Победы, ничьи
        home_wins = sum(1 for _, row in h2h_matches.iterrows()
                        if (row['HomeTeam'] == home_team and row.get('FTHG', 0) > row.get('FTAG', 0)) or
                        (row['AwayTeam'] == home_team and row.get('FTAG', 0) > row.get('FTHG', 0)))

        away_wins = sum(1 for _, row in h2h_matches.iterrows()
                        if (row['HomeTeam'] == away_team and row.get('FTHG', 0) > row.get('FTAG', 0)) or
                        (row['AwayTeam'] == away_team and row.get('FTAG', 0) > row.get('FTHG', 0)))

        draws = len(h2h_matches) - home_wins - away_wins

        features[f'H2H_HomeWins'] = home_wins
        features[f'H2H_AwayWins'] = away_wins
        features[f'H2H_Draws'] = draws

        # Средние голы
        total_goals = sum(row.get('FTHG', 0) + row.get('FTAG', 0) for _, row in h2h_matches.iterrows())
        features[f'H2H_AvgGoals'] = round(total_goals / len(h2h_matches), 2)"""

        stats_to_calc = ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']

        # Итерируем по всем статистикам
        for stat in stats_to_calc:
            home_total = 0
            away_total = 0

            for _, match in h2h_matches.iterrows():
                if match['HomeTeam'] == home_team:
                    home_total += match.get(stat, 0)  # берём значение для хозяев
                    away_total += match.get(stat, 0) if stat != 'FTHG' and stat != 'FTAG' else match.get(stat, 0)
                elif match['AwayTeam'] == home_team:
                    home_total += match.get(stat, 0) if stat != 'FTHG' and stat != 'FTAG' else match.get(stat, 0)
                if match['HomeTeam'] == away_team:
                    away_total += match.get(stat, 0)
                elif match['AwayTeam'] == away_team:
                    away_total += match.get(stat, 0)

            # Среднее значение по H2H
            if len(h2h_matches) > 0:
                features[f'H2H_{stat}_avg'] = round(home_total / len(h2h_matches), 2)
                features[f'H2H_{stat}_avg'] = round(away_total / len(h2h_matches), 2)
            else:
                features[f'H2H_{stat}_avg'] = None
                features[f'H2H_{stat}_avg'] = None

        return features

    def _get_default_features(self, prefix: str, last_n: int) -> Dict:
        """Возвращает дефолтные значения фичей, если нет данных"""
        stats = ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']
        features = {f'{prefix}_Avg{stat}_Last{last_n}': 0.0 for stat in stats}
        features[f'{prefix}_WinRate_Last{last_n}'] = 0.0
        features[f'{prefix}_GoalDiff_Last{last_n}'] = 0.0
        features[f'{prefix}_GoalsScored_Last{last_n}'] = 0.0
        features[f'{prefix}_GoalsConceded_Last{last_n}'] = 0.0
        return features

    def analyze_match(self, home_team: str, away_team: str) -> Dict:
        """
        Главный метод агента: строит фичи и возвращает их вместе с мета-информацией
        """
        features_df = self.build_features_for_match(home_team, away_team)

        if features_df.empty:
            return {
                'success': False,
                'error': 'Не удалось построить фичи'
            }

        return {
            'success': True,
            'home_team': home_team,
            'away_team': away_team,
            'features': features_df,
            'features_dict': features_df.to_dict('records')[0]
        }