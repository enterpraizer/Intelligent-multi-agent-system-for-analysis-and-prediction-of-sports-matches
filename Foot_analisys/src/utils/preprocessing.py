import os
import pandas as pd
import math

# Пути
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
input_file = os.path.join(BASE_DIR, "data/processed/all_matches.csv")
output_file = os.path.join(BASE_DIR, "data/processed/train_full_stats_dataset.csv")

# Параметры Elo
BASE_RATING = 1500
K = 20
HOME_ADV = 50  # временный буст к рейтингу хозяев в ожидании результата[web:22][web:58]

def get_team_rating(team_ratings, team):
    return team_ratings.get(team, BASE_RATING)

def expected_score(R_home, R_away):
    # home advantage учитываем как временный буст[web:22][web:58]
    R_home_eff = R_home + HOME_ADV
    R_away_eff = R_away
    return 1.0 / (1.0 + 10 ** ((R_away_eff - R_home_eff) / 400.0))

def update_elo(R_home, R_away, result):
    """
    result: 'H','D','A'
    """
    exp_home = expected_score(R_home, R_away)
    exp_away = 1.0 - exp_home

    if result == 'H':
        S_home, S_away = 1.0, 0.0
    elif result == 'D':
        S_home, S_away = 0.5, 0.5
    else:  # 'A'
        S_home, S_away = 0.0, 1.0

    # Обновление зависит от разницы "ожидание vs реальный результат" и силы соперника[web:21][web:56]
    R_home_new = R_home + K * (S_home - exp_home)
    R_away_new = R_away + K * (S_away - exp_away)
    return R_home_new, R_away_new

# Загружаем данные
df = pd.read_csv(input_file, parse_dates=['Date'], dayfirst=True)

# Все статистические колонки
stat_cols = ['FTHG', 'FTAG', 'FTR', 'HS', 'AS', 'HST', 'AST',
             'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']

# Отдельно выделим числовые колонки
numeric_cols = [c for c in stat_cols if c != 'FTR']

features_list = []

# Сортируем по дате (важно для Elo и для твоих средних)[web:57]
df = df.sort_values('Date').reset_index(drop=True)

# Словарь текущих рейтингов всех команд
team_ratings = {}

for idx, row in df.iterrows():
    home = row['HomeTeam']
    away = row['AwayTeam']
    match_date = row['Date']
    league = row['league']

    # Текущие рейтинги ПЕРЕД матчем
    R_home = get_team_rating(team_ratings, home)
    R_away = get_team_rating(team_ratings, away)

    # Сохраняем рейтинги как фичи
    home_elo = R_home
    away_elo = R_away
    diff_elo = home_elo - away_elo

    # последние 10 матчей команды-хозяина
    home_past = df[((df['HomeTeam'] == home) | (df['AwayTeam'] == home)) &
                   (df['Date'] < match_date)].sort_values('Date', ascending=False).head(10)

    # последние 10 матчей команды-гостя
    away_past = df[((df['HomeTeam'] == away) | (df['AwayTeam'] == away)) &
                   (df['Date'] < match_date)].sort_values('Date', ascending=False).head(10)

    # последние личные встречи (можно ограничить, но не обязательно)
    h2h = df[
        (((df['HomeTeam'] == home) & (df['AwayTeam'] == away)) |
         ((df['HomeTeam'] == away) & (df['AwayTeam'] == home))) &
        (df['Date'] < match_date)
    ].sort_values('Date', ascending=False)

    # Средние фичи последних матчей хозяев
    home_features = {
        f'Home_{col}_avg': pd.to_numeric(home_past[col], errors='coerce').mean()
        for col in numeric_cols if col in home_past.columns
    }

    # Средние фичи последних матчей гостей
    away_features = {
        f'Away_{col}_avg': pd.to_numeric(away_past[col], errors='coerce').mean()
        for col in numeric_cols if col in away_past.columns
    }

    # Средние фичи последних личных встреч
    h2h_features = {
        f'H2H_{col}_avg': pd.to_numeric(h2h[col], errors='coerce').mean()
        for col in numeric_cols if col in h2h.columns
    }

    # Таргеты — вся статистика текущего матча
    target_stats = {f'Target_{col}': row[col] for col in stat_cols if col in row.index}

    # Собираем всё в один словарь
    features = {
        'Date': match_date,
        'HomeTeam': home,
        'AwayTeam': away,
        'Home_Elo': home_elo,
        'Away_Elo': away_elo,
        'Diff_Elo': diff_elo,
    }
    features.update(home_features)
    features.update(away_features)
    features.update(h2h_features)
    features.update(target_stats)

    features_list.append(features)

    # ОБНОВЛЯЕМ рейтинги ПОСЛЕ матча, чтобы этот матч повлиял на следующие[web:21][web:56]
    ftr = row['FTR']  # исход матча
    R_home_new, R_away_new = update_elo(R_home, R_away, ftr)
    team_ratings[home] = R_home_new
    team_ratings[away] = R_away_new

# Создаем итоговый DataFrame
train_df = pd.DataFrame(features_list)

# Чистим пропуски (как и раньше)
train_df = train_df.dropna()

# Сохраняем
train_df.to_csv(output_file, index=False)
print("✅ Готовый датасет со всеми таргетами и Elo сохранен в:", output_file)
print("Размер:", train_df.shape)
