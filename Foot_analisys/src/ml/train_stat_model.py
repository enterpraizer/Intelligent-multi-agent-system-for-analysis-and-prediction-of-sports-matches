# src/ml/train_models.py
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
import joblib

def train_all_models(dataset_path: str, models_dir: str, n_estimators: int = 200):
    os.makedirs(models_dir, exist_ok=True)

    # -----------------------------
    # Загружаем датасет
    # -----------------------------
    df = pd.read_csv(dataset_path, parse_dates=['Date'], dayfirst=True)

    # Признаки и таргеты
    feature_cols = [col for col in df.columns if col.startswith(('Home_', 'Away_', 'H2H_'))]
    target_cols = [
        "Target_FTHG", "Target_FTAG",
        "Target_HS", "Target_AS", "Target_HST", "Target_AST",
        "Target_HF", "Target_AF", "Target_HC", "Target_AC",
        "Target_HY", "Target_AY", "Target_HR", "Target_AR"
    ]

    # Убираем NaN
    df = df.dropna(subset=feature_cols + target_cols).reset_index(drop=True)

    X = df[feature_cols]
    y = df[target_cols]

    print("Признаки:", X.shape)
    print("Таргеты:", y.shape)
    print(f"После очистки осталось {len(df)} матчей")

    results = {}  # Для анализа ошибок

    for target in target_cols:
        print(f"Обучаем модель для: {target}")

        # Разделение на train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y[target], test_size=0.2, random_state=42
        )

        # XGBoost модель
        model = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=10,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Предсказание
        y_pred = model.predict(X_test)

        # MAE
        mae = mean_absolute_error(y_test, y_pred)
        print(f"MAE для {target}: {mae:.2f}")

        # Сохраняем модель
        model_path = os.path.join(models_dir, f"{target}.pkl")
        joblib.dump(model, model_path)

        # Для анализа
        results[target] = (y_test, y_pred)

    # -----------------------------
    # Таблица для первых 5 матчей
    # -----------------------------
    comparison_rows = 5
    comparison_data = []
    for target, (y_test, y_pred) in results.items():
        comp_df = pd.DataFrame({
            'Target': [target]*comparison_rows,
            'Actual': y_test.iloc[:comparison_rows].values,
            'Predicted': y_pred[:comparison_rows]
        })
        comparison_data.append(comp_df)

    comparison_df = pd.concat(comparison_data, ignore_index=True)
    print("\nПример сравнения реальных и предсказанных значений (5 матчей на таргет):")
    print(comparison_df)

    return comparison_df

# -----------------------------
# Точка входа
# -----------------------------
if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    dataset_path = os.path.join(BASE_DIR, "data/processed/train_full_stats_dataset.csv")
    models_dir = os.path.join(BASE_DIR, "models")

    train_all_models(dataset_path, models_dir)
