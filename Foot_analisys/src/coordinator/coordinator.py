from src.agents.predictor import PredictorAgent
from src.agents.reporter import ReporterLLM
import pandas as pd


class Coordinator:
    """
    Координатор для работы с матчами.
    Связывает PredictorAgent и ReporterLLM.
    """

    def __init__(self, models_dir=None):
        self.predictor_agent = PredictorAgent(models_dir=models_dir)
        self.reporter_llm = ReporterLLM(models_dir=models_dir)

    def predict_single_match(self, match_features: pd.DataFrame) -> dict:
        """
        Прогноз для одного матча и формирование структурированного отчёта.
        """
        if match_features.shape[0] != 1:
            raise ValueError("match_features должен содержать одну строку")

        # Предсказание
        preds = self.predictor_agent.predict_match(match_features)

        # Формируем структурированный отчёт
        report = self.reporter_llm.generate_structured_report(match_features)
        return report

    def predict_batch(self, df_features: pd.DataFrame) -> list[dict]:
        """
        Прогноз для батча матчей и формирование списка отчётов.
        """
        return self.reporter_llm.generate_batch_structured_report(df_features)


# -----------------------------
# Пример использования
# -----------------------------
if __name__ == "__main__":
    # Пример одного матча
    sample_match = pd.DataFrame([{
        'HomeTeam': 'Team A',
        'AwayTeam': 'Team B',
        'Home_HS_avg_5': 12,
        'Home_AS_avg_5': 11,
        'Home_HST_avg_5': 6,
        'Home_AST_avg_5': 5,
        'Home_HF_avg_5': 10,
        'Home_AF_avg_5': 8,
        'Home_HC_avg_5': 4,
        'Home_AC_avg_5': 3,
        'Home_HY_avg_5': 1,
        'Home_AY_avg_5': 2,
        'Home_HR_avg_5': 0,
        'Home_AR_avg_5': 0,
        'Away_HS_avg_5': 10,
        'Away_AS_avg_5': 12,
        'Away_HST_avg_5': 5,
        'Away_AST_avg_5': 6,
        'Away_HF_avg_5': 9,
        'Away_AF_avg_5': 11,
        'Away_HC_avg_5': 3,
        'Away_AC_avg_5': 4,
        'Away_HY_avg_5': 2,
        'Away_AY_avg_5': 1,
        'Away_HR_avg_5': 0,
        'Away_AR_avg_5': 0,
        'H2H_FTHG_avg_5': 1.5,
        'H2H_FTAG_avg_5': 1.2
    }])

    coordinator = Coordinator(models_dir="src/ml/models")
    report = coordinator.predict_single_match(sample_match)
    print(report)
