from src.agents.predictor import PredictorAgent
import pandas as pd

class ReporterLLM:
    """
    Формирование структурированных данных для LLM по матчам.
    """

    def __init__(self, models_dir=None):
        self.predictor = PredictorAgent(models_dir=models_dir)

    def generate_structured_report(self, match_features: pd.DataFrame) -> dict:
        """
        Возвращает словарь с предсказанными статистиками для одного матча.
        """
        preds = self.predictor.predict_match(match_features)
        report = {
            "HomeTeam": match_features['HomeTeam'].iloc[0],
            "AwayTeam": match_features['AwayTeam'].iloc[0],
            "PredictedStats": {
                "Goals": {
                    "Home": preds['Target_FTHG'],
                    "Away": preds['Target_FTAG']
                },
                "Shots": {
                    "Home": preds['Target_HS'],
                    "Away": preds['Target_AS']
                },
                "ShotsOnTarget": {
                    "Home": preds['Target_HST'],
                    "Away": preds['Target_AST']
                },
                "Fouls": {
                    "Home": preds['Target_HF'],
                    "Away": preds['Target_AF']
                },
                "Corners": {
                    "Home": preds['Target_HC'],
                    "Away": preds['Target_AC']
                },
                "YellowCards": {
                    "Home": preds['Target_HY'],
                    "Away": preds['Target_AY']
                },
                "RedCards": {
                    "Home": preds['Target_HR'],
                    "Away": preds['Target_AR']
                }
            }
        }
        return report

    def generate_batch_structured_report(self, df_features: pd.DataFrame) -> list[dict]:
        """
        Для батча матчей возвращает список словарей с предсказанными статистиками.
        """
        reports = []
        for i, row in df_features.iterrows():
            row_df = pd.DataFrame([row])
            report = self.generate_structured_report(row_df)
            reports.append(report)
        return reports


# -----------------------------
# Пример использования
# -----------------------------
if __name__ == "__main__":
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

    reporter = ReporterLLM()
    report = reporter.generate_structured_report(sample_match)
    print(report)
