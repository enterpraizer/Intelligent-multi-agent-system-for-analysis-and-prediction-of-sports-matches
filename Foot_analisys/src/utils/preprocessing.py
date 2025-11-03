import os
import pandas as pd


# Пути
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
input_file = os.path.join(BASE_DIR, "data/processed/all_matches.csv")
output_file = os.path.join(BASE_DIR, "data/processed/train_full_stats_dataset.csv")


# Загружаем данные
df = pd.read_csv(input_file, parse_dates=['Date'], dayfirst=True)

# Все статистические колонки
stat_cols = ['FTHG', 'FTAG', 'FTR', 'HS', 'AS', 'HST', 'AST',
             'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']

# Отдельно выделим числовые колонки
numeric_cols = [c for c in stat_cols if c != 'FTR']

features_list = []

# Сортируем по дате
df = df.sort_values('Date')

for idx, row in df.iterrows():
    home = row['HomeTeam']
    away = row['AwayTeam']
    match_date = row['Date']
    league = row['league']
    # последние 5 матчей команды-хозяина
    home_past = df[((df['HomeTeam'] == home) | (df['AwayTeam'] == home)) &
                   (df['Date'] < match_date)].sort_values('Date', ascending=False).head(10)


    # последние 5 матчей команды-гостя
    away_past = df[((df['HomeTeam'] == away) | (df['AwayTeam'] == away)) &
                   (df['Date'] < match_date)].sort_values('Date', ascending=False).head(10)

    # последние 5 личных встреч (H2H)
    h2h = df[
        (((df['HomeTeam'] == home) & (df['AwayTeam'] == away)) |
         ((df['HomeTeam'] == away) & (df['AwayTeam'] == home))) &
        (df['Date'] < match_date)
    ].sort_values('Date', ascending=False)

    # Средние фичи последних 5 матчей хозяев (только числовые)
    home_features = {f'Home_{col}_avg': pd.to_numeric(home_past[col], errors='coerce').mean()
                     for col in numeric_cols if col in home_past.columns}

    # Средние фичи последних 5 матчей гостей
    away_features = {f'Away_{col}_avg': pd.to_numeric(away_past[col], errors='coerce').mean()
                     for col in numeric_cols if col in away_past.columns}

    # Средние фичи последних 5 личных встреч
    h2h_features = {f'H2H_{col}_avg': pd.to_numeric(h2h[col], errors='coerce').mean()
                    for col in numeric_cols if col in h2h.columns}

    # Таргеты — вся статистика текущего матча (включая FTR)
    target_stats = {f'Target_{col}': row[col] for col in stat_cols if col in row.index}

    # Собираем все в один словарь
    features = {
        'Date': match_date,
        'HomeTeam': home,
        'AwayTeam': away
    }
    features.update(home_features)
    features.update(away_features)
    features.update(h2h_features)
    features.update(target_stats)

    features_list.append(features)

# Создаем итоговый DataFrame
train_df = pd.DataFrame(features_list)

train_df=train_df.dropna()

# Сохраняем
train_df.to_csv(output_file, index=False)
print("✅ Готовый датасет со всеми таргетами сохранен в:", output_file)
print("Размер:", train_df.shape)
