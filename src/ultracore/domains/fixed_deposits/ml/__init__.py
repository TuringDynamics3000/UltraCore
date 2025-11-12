"""Machine Learning for Fixed Deposits"""
from .fraud_detector import FDFraudDetector
from .renewal_predictor import RenewalPredictionModel
from .churn_predictor import CustomerChurnPredictor
from .rate_optimizer import InterestRateOptimizer

__all__ = [
    "FDFraudDetector",
    "RenewalPredictionModel",
    "CustomerChurnPredictor",
    "InterestRateOptimizer",
]
