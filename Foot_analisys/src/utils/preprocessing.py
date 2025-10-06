import os
import pandas as pd

# Пути
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
input_file = os.path.join(BASE_DIR, "data/processed/all_matches.csv")
output_file = os.path.join(BASE_DIR, "data/processed/train_dataset.csv")

# Загружаем данные
df = pd.read_csv(input_file, parse_dates=['Date'], dayfirst=True)

# Колонки статистики для усреднения
stat_cols = ['HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']

features_list = []

# Сортируем по дате для удобства
df = df.sort_values('Date')

for idx, row in df.iterrows():
    home = row['HomeTeam']
    away = row['AwayTeam']
    match_date = row['Date']

    # последние 5 матчей команды-хозяина
    home_past = df[((df['HomeTeam']==home) | (df['AwayTeam']==home)) & (df['Date'] < match_date)].sort_values('Date', ascending=False).head(5)
    if len(home_past) < 5:
        continue

    # последние 5 матчей команды-гостя
    away_past = df[((df['HomeTeam']==away) | (df['AwayTeam']==away)) & (df['Date'] < match_date)].sort_values('Date', ascending=False).head(5)
    if len(away_past) < 5:
        continue

    # последние 5 H2H
    h2h = df[
        (((df['HomeTeam']==home) & (df['AwayTeam']==away)) |
         ((df['HomeTeam']==away) & (df['AwayTeam']==home))) &
        (df['Date'] < match_date)
    ].sort_values('Date', ascending=False).head(5)
    if len(h2h) < 5:
        continue

    # Средние фичи последних 5 матчей команды-хозяина
    home_features = {f'Home_{col}_avg_5': home_past.apply(lambda x: x[col] if x.name in home_past.index else x[col], axis=1).mean() for col in stat_cols}

    # Средние фичи последних 5 матчей команды-гостя
    away_features = {f'Away_{col}_avg_5': away_past.apply(lambda x: x[col] if x.name in away_past.index else x[col], axis=1).mean() for col in stat_cols}

    # Средние фичи H2H
    h2h_features = {f'H2H_{col}_avg_5': h2h[col].mean() for col in ['FTHG', 'FTAG']}

    # Собираем все в один словарь
    features = {
        'Date': match_date,
        'Time': row.get('Time', None),
        'HomeTeam': home,
        'AwayTeam': away,
        'FTR': row['FTR']
    }
    features.update(home_features)
    features.update(away_features)
    features.update(h2h_features)

    features_list.append(features)

# Создаем итоговый DataFrame
train_df = pd.DataFrame(features_list)

# Сохраняем в CSV
train_df.to_csv(output_file, index=False)
print("Готовый датасет для обучения сохранен:", output_file)
