{"id":"58392","variant":"standard","title":"MatchPredictor (CatBoost)"}
import os
import joblib
import pandas as pd
from catboost import CatBoostRegressor


class MatchPredictor:
    """
    Класс для предсказания статистики матчей с учётом
    формата моделей CatBoost (*.cbm) и структуры проекта.
    """

    def __init__(self, models_dir=None):

        # Ищем корень проекта по папке models_catboost
        if models_dir is None:
            curr_dir = os.path.abspath(os.path.dirname(__file__))

            while True:
                candidate = os.path.join(curr_dir, "models_catboost")
                if os.path.exists(candidate):
                    models_dir = candidate
                    break

                parent = os.path.dirname(curr_dir)
                if parent == curr_dir:
                    raise FileNotFoundError("Не найдена папка models_catboost")
                curr_dir = parent

        self.models_dir = models_dir

        self.target_cols = [
            "Target_FTHG", "Target_FTAG",
            "Target_HS", "Target_AS",
            "Target_HST", "Target_AST",
            "Target_HF", "Target_AF",
            "Target_HC", "Target_AC",
            "Target_HY", "Target_AY",
            "Target_HR", "Target_AR"
        ]

        # Фичи должны совпадать с train_models.py
        self.feature_cols = None  # Определим при первом predict

        self.models = {}
        self._load_models()

    def _load_models(self):
        """Загружаем все модели CatBoost (*.cbm)"""
        print(f"🔍 Загружаем модели из: {self.models_dir}")

        for target in self.target_cols:
            model_path = os.path.join(self.models_dir, f"{target}.cbm")

            if os.path.exists(model_path):
                model = CatBoostRegressor()
                model.load_model(model_path)
                self.models[target] = model
                print(f"✅ {target} загружена")
            else:
                print(f"⚠️ Модель {target} не найдена ({model_path})")

    def _extract_feature_cols(self, df: pd.DataFrame):
        """
        Достаём feature_cols как в train_models.py
        """
        return [
            col for col in df.columns
            if col.startswith(("Home_", "Away_", "H2H_")) and col.endswith("_avg")
        ]

    def predict_match(self, match_features: pd.DataFrame):
        """
        Предсказывает статистику одного матча (одна строка).
        """

        if self.feature_cols is None:
            self.feature_cols = self._extract_feature_cols(match_features)

        X = match_features[self.feature_cols]

        predictions = {}
        for target, model in self.models.items():
            predictions[target] = float(model.predict(X)[0])

        return predictions

    def predict_batch(self, df_features: pd.DataFrame):
        """
        Предсказывает статистику для батча матчей (df).
        """
        if self.feature_cols is None:
            self.feature_cols = self._extract_feature_cols(df_features)

        result = []

        for _, row in df_features.iterrows():
            row_df = pd.DataFrame([row])
            result.append(self.predict_match(row_df))

        return pd.DataFrame(result)
