import os
import pandas as pd

# Папка проекта
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Исходные данные
input_root = os.path.join(BASE_DIR, "data/raw")
# Папка для обработанных данных
processed_root = os.path.join(BASE_DIR, "data/processed")
os.makedirs(processed_root, exist_ok=True)

# Столбцы, которые оставляем
columns_to_keep = [
    "Date", "Time",
    "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR",
    "HS", "AS", "HST", "AST",
    "HF", "AF", "HC", "AC",
    "HY", "AY", "HR", "AR"
]

# Список для объединения всех CSV
all_dfs = []

# Проходим по всем лигам
for league in os.listdir(input_root):
    league_path = os.path.join(input_root, league)
    if not os.path.isdir(league_path):
        continue

    output_league_path = os.path.join(processed_root, league)
    os.makedirs(output_league_path, exist_ok=True)

    # Проходим по всем сезонам
    for file in os.listdir(league_path):
        if not file.endswith(".csv"):
            continue
        file_path = os.path.join(league_path, file)
        df = pd.read_csv(file_path)

        # Оставляем только существующие нужные столбцы
        existing_cols = [col for col in columns_to_keep if col in df.columns]
        df = df[existing_cols]
        df['league'] = league
        # Сохраняем отдельный CSV
        output_file = os.path.join(output_league_path, file)
        df.to_csv(output_file, index=False)

        # Добавляем в общий список для объединения
        all_dfs.append(df)
        print(f"Обработан файл: {file_path}, оставлено {len(existing_cols)} колонок")

# Объединяем все в один DataFrame
full_df = pd.concat(all_dfs, ignore_index=True)

def fix_two_digit_year(date_str):
    """Преобразует даты с двухзначным годом в формат DD/MM/YYYY"""
    if pd.isna(date_str):  # пропуски оставляем как есть
        return date_str
    date_str = str(date_str).strip()
    parts = date_str.split('/')
    if len(parts) != 3:
        return date_str  # если формат неправильный, возвращаем как есть
    day, month, year = parts
    if len(year) == 2:
        # добавляем "20" перед годом, если год <= 50, иначе "19"
        year_int = int(year)
        if year_int <= 50:
            year = f"20{year}"
        else:
            year = f"19{year}"
    return f"{day}/{month}/{year}"

# 1. Привести всё к строкам и убрать лишние пробелы
full_df['Date'] = full_df['Date'].astype(str).str.strip()

full_df['Date'] = full_df['Date'].apply(fix_two_digit_year)

# 2. Преобразовать с dayfirst=True (европейский формат)
full_df['Date'] = pd.to_datetime(full_df['Date'], dayfirst=True)

# 3. Сортировка по дате
full_df = full_df.sort_values(by='Date').reset_index(drop=True)



# Сохраняем объединённый CSV
full_dataset_path = os.path.join(processed_root, "all_matches.csv")
full_df.to_csv(full_dataset_path, index=False)

print("Все файлы объединены в один датасет:", full_dataset_path)
