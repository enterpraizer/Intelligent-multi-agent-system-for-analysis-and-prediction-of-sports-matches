"""
Агент-прогнозист: получает фичи от аналитика и делает предикт
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.predict import MatchPredictor
import pandas as pd
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PredictorAgent:
    """Агент получает фичи и вызывает MatchPredictor"""

    def __init__(self):
        self.predictor = MatchPredictor()
        logger.info(f"PredictorAgent: загружено моделей {len(self.predictor.models)}")

    def predict(self, features: pd.DataFrame) -> Dict:
        """
        Получает фичи от Analyst и делает предикт через MatchPredictor
        Возвращает все предсказания моделей
        """
        logger.info("Делаю предикт через MatchPredictor")

        try:
            # Вызываем ТВОЙ predict_match
            raw_predictions = self.predictor.predict_match(features)

            logger.info(f"✓ Предикт готов, получено значений: {len(raw_predictions)}")

            return {
                'success': True,
                'predictions': raw_predictions
            }

        except Exception as e:
            logger.error(f"Ошибка предикта: {e}")
            return {
                'success': False,
                'error': str(e)
            }