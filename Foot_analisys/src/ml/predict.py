import os
import joblib
import pandas as pd

class MatchPredictor:
    """
    Класс для предсказания статистики матчей на основе обученных моделей.
    """

    def __init__(self, models_dir=None):
        if models_dir is None:
            # По умолчанию смотрим в папку ml/models
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
            models_dir = os.path.join(base_dir, "models")
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
        for target in self.target_cols:
            model_path = os.path.join(self.models_dir, f"{target}.joblib")
            if os.path.exists(model_path):
                self.models[target] = joblib.load(model_path)
            else:
                print(f"[Warning] Модель для {target} не найдена в {model_path}")

    def predict_match(self, match_features: pd.DataFrame):
        """
        Предсказывает статистику для одного матча.
        match_features: pd.DataFrame с одной строкой (X-фичи)
        Возвращает dict {target: prediction}
        """
        predictions = {}
        for target, model in self.models.items():
            if target in match_features.columns:
                # Убираем целевую колонку из фичей
                X = match_features.drop(columns=[target], errors='ignore')
            else:
                X = match_features
            pred = model.predict(X)[0]
            predictions[target] = pred
        return predictions

    def predict_batch(self, df_features: pd.DataFrame):
        """
        Предсказывает статистику для батча матчей.
        Возвращает DataFrame с предсказанными значениями.
        """
        all_preds = []
        for i, row in df_features.iterrows():
            row_df = pd.DataFrame([row])
            preds = self.predict_match(row_df)
            all_preds.append(preds)
        return pd.DataFrame(all_preds)
