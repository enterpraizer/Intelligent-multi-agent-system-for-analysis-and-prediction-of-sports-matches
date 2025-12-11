import os
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error


def train_all_models(dataset_path: str, models_dir: str):
    os.makedirs(models_dir, exist_ok=True)

    df = pd.read_csv(dataset_path, parse_dates=['Date'], dayfirst=True)

    df = df.sort_values("Date").reset_index(drop=True)

    feature_cols = [
        col for col in df.columns
        if col.startswith(("Home_", "Away_", "H2H_")) and col.endswith("_avg")
    ]

    feature_cols += ["Home_Elo", "Away_Elo", "Diff_Elo"]

    target_cols = [
        "Target_FTHG", "Target_FTAG",
        "Target_HS", "Target_AS",
        "Target_HST", "Target_AST",
        "Target_HF", "Target_AF",
        "Target_HC", "Target_AC",
        "Target_HY", "Target_AY",
        "Target_HR", "Target_AR"
    ]


    df = df.dropna(subset=feature_cols + target_cols).reset_index(drop=True)

    print(f"Матчей после очистки: {len(df)}")
    print(f"Количество фичей: {len(feature_cols)}")

    weighted_stats = ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST']
    for col in feature_cols:
        for stat in weighted_stats:
            if col.endswith(f"{stat}_avg"):
                if col.startswith("H2H_"):
                    df[col] = df[col] * 0.7
                elif col.startswith("Home_") or col.startswith("Away_"):
                    df[col] = df[col] * 0.3
                break

    train_size = int(len(df) * 0.8)
    train = df.iloc[:train_size]
    test = df.iloc[train_size:]

    results = {}

    for target in target_cols:
        print(f"\n=== Обучаем модель для {target} ===")

        X_train = train[feature_cols]
        y_train = train[target]

        X_test = test[feature_cols]
        y_test = test[target]

        model = CatBoostRegressor(
            iterations=600,
            depth=8,
            learning_rate=0.05,
            loss_function="MAE",
            verbose=False,
            random_seed=42
        )

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)

        print(f"MAE: {mae:.4f}")

        model_path = os.path.join(models_dir, f"{target}.cbm")
        model.save_model(model_path)

        results[target] = (y_test, y_pred)

    print("\nОбучение всех моделей завершено.")
    return results


if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    dataset_path = os.path.join(BASE_DIR, "data/processed/train_full_stats_dataset.csv")
    models_dir = os.path.join(BASE_DIR, "models_catboost")

    train_all_models(dataset_path, models_dir)
