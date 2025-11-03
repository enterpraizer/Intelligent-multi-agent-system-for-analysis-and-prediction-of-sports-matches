import os
import joblib
import pandas as pd

class MatchPredictor:
    """
    Класс для предсказания статистики матчей на основе обученных моделей.
    """

    def __init__(self, models_dir=None):

            # Ищем корень проекта по наличию папки 'models'
        curr_dir = os.path.abspath(os.path.dirname(__file__))
        while True:
            if os.path.exists(os.path.join(curr_dir, "models")):
                models_dir = os.path.join(curr_dir, "models")
                break
            parent = os.path.dirname(curr_dir)
            if parent == curr_dir:
                raise FileNotFoundError("Не удалось найти папку 'models' в корне проекта")
            curr_dir = parent

        self.models_dir = models_dir
        self.models = {}
        self.target_cols = [
            "Target_FTHG", "Target_FTAG",
            "Target_HS", "Target_AS", "Target_HST", "Target_AST",
            "Target_HF", "Target_AF", "Target_HC", "Target_AC",
            "Target_HY", "Target_AY", "Target_HR", "Target_AR"
        ]
        self._load_models()

    def _load_models(self):
        """Загружаем все модели из папки"""
        print(f"🔍 Ищем модели в: {self.models_dir}")
        for target in self.target_cols:
            model_path = os.path.join(self.models_dir, f"{target}.pkl")
            if os.path.exists(model_path):
                self.models[target] = joblib.load(model_path)
                print(f"✅ Загружена модель: {target}")
            else:
                print(f"⚠️ Модель для {target} не найдена ({model_path})")

    def predict_match(self, match_features: pd.DataFrame):
        """Предсказывает статистику для одного матча"""
        predictions = {}
        for target, model in self.models.items():
            X = match_features.drop(columns=[target], errors='ignore')
            predictions[target] = model.predict(X)[0]
        return predictions

    def predict_batch(self, df_features: pd.DataFrame):
        """Предсказывает статистику для батча матчей"""
        return pd.DataFrame([self.predict_match(pd.DataFrame([row])) for _, row in df_features.iterrows()])
