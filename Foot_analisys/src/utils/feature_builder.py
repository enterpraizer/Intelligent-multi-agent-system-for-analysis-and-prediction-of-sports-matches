import pandas as pd


class FeatureBuilder:
    """
    Создание X-фич для нового матча на основе исторических данных.
    """

    def __init__(self, historical_data_path: str):
        # Загружаем исторические матчи
        self.df_matches = pd.read_csv(historical_data_path, parse_dates=['Date'], dayfirst=True)

    def build_features_for_match(self, home_team: str, away_team: str) -> pd.DataFrame:
        """
        Возвращает DataFrame с одной строкой X-фич для заданного матча.
        """

        # Берём последние 5 матчей команды
        def get_last_n_avg(team, n=5):
            last_matches = self.df_matches[
                (self.df_matches['HomeTeam'] == team) | (self.df_matches['AwayTeam'] == team)
                ].sort_values(by='Date', ascending=False).head(n)

            # Средние значения по интересующим колонкам
            features = {}
            for stat in ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']:
                # Для домашней команды
                home_stat = last_matches.apply(
                    lambda row: row[f'Home_{stat}'] if row['HomeTeam'] == team else row[f'Away_{stat}'], axis=1
                ).mean()
                features[f"{team}_{stat}_avg_{n}"] = home_stat
            return features

        # Фичи для домашней и гостевой команды
        home_features = get_last_n_avg(home_team)
        away_features = get_last_n_avg(away_team)

        # Фичи H2H (среднее за последние 5 очных матчей)
        h2h_matches = self.df_matches[
            ((self.df_matches['HomeTeam'] == home_team) & (self.df_matches['AwayTeam'] == away_team)) |
            ((self.df_matches['HomeTeam'] == away_team) & (self.df_matches['AwayTeam'] == home_team))
            ].sort_values(by='Date', ascending=False).head(5)

        h2h_features = {}
        for stat in ['FTHG', 'FTAG']:
            if len(h2h_matches) == 0:
                h2h_features[f"H2H_{stat}_avg_5"] = 0.0
            else:
                h2h_features[f"H2H_{stat}_avg_5"] = h2h_matches.apply(
                    lambda row: row[f'Home_{stat}'] if row['HomeTeam'] == home_team else row[f'Away_{stat}'], axis=1
                ).mean()

        # Объединяем все фичи
        features = {}
        features.update({f"Home_{k.split('_', 1)[1]}_avg_5": v for k, v in home_features.items()})
        features.update({f"Away_{k.split('_', 1)[1]}_avg_5": v for k, v in away_features.items()})
        features.update(h2h_features)

        # Добавляем команды
        features['HomeTeam'] = home_team
        features['AwayTeam'] = away_team

        return pd.DataFrame([features])


# -----------------------------
# Пример использования
# -----------------------------
if __name__ == "__main__":
    builder = FeatureBuilder("src/data/processed/train_full_stats_dataset.csv")
    df_feat = builder.build_features_for_match("Team A", "Team B")
    print(df_feat)
