import pandas as pd
from src.ml.predict import MatchPredictor

class PredictorAgent:
    """
    Агент для получения предсказаний статистики матчей.
    Использует ml/predict.py
    """

    def __init__(self, models_dir=None):
        self.predictor = MatchPredictor(models_dir=models_dir)

    def predict_match(self, match_features: pd.DataFrame):
        """
        match_features: pd.DataFrame с одной строкой (X-фичи)
        Возвращает dict с предсказанной статистикой
        """
        if match_features.shape[0] != 1:
            raise ValueError("match_features должен содержать только один матч (одну строку)")
        return self.predictor.predict_match(match_features)

    def predict_batch(self, df_features: pd.DataFrame):
        """
        df_features: pd.DataFrame с несколькими матчами
        Возвращает DataFrame с предсказанной статистикой
        """
        return self.predictor.predict_batch(df_features)

# -----------------------------
# Пример использования
# -----------------------------
if __name__ == "__main__":
    # Пример одного матча
    sample = pd.DataFrame([{
        'Home_HS_avg_5': 12.0,
        'Home_AS_avg_5': 11.0,
        'Home_HST_avg_5': 6.0,
        'Home_AST_avg_5': 5.0,
        'Home_HF_avg_5': 10.0,
        'Home_AF_avg_5': 8.0,
        'Home_HC_avg_5': 4.0,
        'Home_AC_avg_5': 3.0,
        'Home_HY_avg_5': 1.0,
        'Home_AY_avg_5': 2.0,
        'Home_HR_avg_5': 0.0,
        'Home_AR_avg_5': 0.0,
        'Away_HS_avg_5': 10.0,
        'Away_AS_avg_5': 12.0,
        'Away_HST_avg_5': 5.0,
        'Away_AST_avg_5': 6.0,
        'Away_HF_avg_5': 9.0,
        'Away_AF_avg_5': 11.0,
        'Away_HC_avg_5': 3.0,
        'Away_AC_avg_5': 4.0,
        'Away_HY_avg_5': 2.0,
        'Away_AY_avg_5': 1.0,
        'Away_HR_avg_5': 0.0,
        'Away_AR_avg_5': 0.0,
        'H2H_FTHG_avg_5': 1.5,
        'H2H_FTAG_avg_5': 1.2
    }])

    agent = PredictorAgent()
    preds = agent.predict_match(sample)
    print(preds)
