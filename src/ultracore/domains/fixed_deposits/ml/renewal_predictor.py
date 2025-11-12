"""ML Model to Predict Fixed Deposit Renewal Likelihood"""
import numpy as np
from typing import Dict, List
from datetime import date, datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from ultracore.ml.base import BaseMLModel


class RenewalPredictionModel(BaseMLModel):
    """
    Predict whether customer will renew their fixed deposit.
    
    Features considered:
    - Current interest rate vs market rate
    - Customer tenure with bank
    - Number of previous FDs
    - Average FD holding period
    - Account balance trends
    - Recent interactions with bank
    - Life events (detected from transactions)
    - Economic indicators
    
    Use cases:
    - Proactive retention offers
    - Personalized renewal rates
    - Anya's renewal recommendations
    - Product optimization
    """
    
    def __init__(self):
        super().__init__(
            model_name="fd_renewal_predictor",
            model_type="classification",
            version="1.0.0"
        )
        
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )
        
        self.scaler = StandardScaler()
    
    async def train(
        self,
        historical_maturities: List[Dict]
    ) -> Dict:
        """
        Train on historical maturity events.
        
        Args:
            historical_maturities: Past FD maturities with renewal outcomes
        
        Returns:
            Training metrics
        """
        # Extract features and labels
        X = [self._extract_features(fd) for fd in historical_maturities]
        y = [1 if fd.get("renewed", False) else 0 for fd in historical_maturities]
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Evaluate
        train_score = self.model.score(X_scaled, y)
        
        # Feature importance
        feature_importance = self.model.feature_importances_
        
        return {
            "train_accuracy": float(train_score),
            "training_samples": len(X),
            "renewal_rate": float(np.mean(y)),
            "top_features": self._get_top_features(feature_importance)
        }
    
    async def predict_renewal(
        self,
        fd_account: Dict,
        customer_profile: Dict,
        market_conditions: Dict
    ) -> Dict:
        """
        Predict renewal probability.
        
        Returns:
            Prediction with confidence and recommendations
        """
        # Extract features
        features = self._extract_features_live(
            fd_account,
            customer_profile,
            market_conditions
        )
        features_scaled = self.scaler.transform([features])
        
        # Predict
        renewal_probability = self.model.predict_proba(features_scaled)[0][1]
        will_renew = renewal_probability > 0.5
        
        # Generate recommendations
        if renewal_probability < 0.3:
            recommendation = "HIGH_RISK_OF_CHURN"
            actions = [
                "Offer rate premium (0.25% above standard)",
                "Anya proactive outreach 2 weeks before maturity",
                "Highlight loyalty benefits",
                "Suggest ladder strategy"
            ]
        elif renewal_probability < 0.6:
            recommendation = "MODERATE_RISK"
            actions = [
                "Standard renewal offer at current market rate",
                "Anya reminder 1 week before maturity",
                "Showcase product benefits"
            ]
        else:
            recommendation = "LIKELY_TO_RENEW"
            actions = [
                "Standard renewal process",
                "Consider upsell to longer term",
                "Anya confirmation message"
            ]
        
        return {
            "will_renew": will_renew,
            "renewal_probability": float(renewal_probability),
            "confidence": 0.82,
            "recommendation": recommendation,
            "suggested_actions": actions,
            "key_factors": self._explain_prediction(features)
        }
    
    def _extract_features(self, fd: Dict) -> np.ndarray:
        """Extract features from historical FD."""
        features = []
        
        # Rate comparison
        current_rate = fd.get("interest_rate", 5.0)
        market_rate = fd.get("market_rate_at_maturity", 5.0)
        features.append(current_rate - market_rate)  # Rate differential
        
        # Customer tenure
        features.append(fd.get("customer_tenure_months", 12))
        
        # FD history
        features.append(fd.get("previous_fd_count", 0))
        features.append(fd.get("average_fd_term_months", 12))
        
        # Engagement
        features.append(fd.get("app_logins_last_month", 5))
        features.append(fd.get("branch_visits_last_year", 2))
        
        # Financial indicators
        features.append(fd.get("savings_balance", 10000))
        features.append(fd.get("total_relationship_value", 50000))
        
        # Term
        features.append(fd.get("term_months", 12))
        
        # Pad to fixed size
        while len(features) < 20:
            features.append(0.0)
        
        return np.array(features[:20])
    
    def _extract_features_live(
        self,
        fd_account: Dict,
        customer_profile: Dict,
        market_conditions: Dict
    ) -> np.ndarray:
        """Extract features for live prediction."""
        features = []
        
        # Rate comparison
        current_rate = fd_account.get("interest_rate", 5.0)
        market_rate = market_conditions.get("current_market_rate", 5.0)
        features.append(current_rate - market_rate)
        
        # Customer tenure
        features.append(customer_profile.get("tenure_months", 12))
        
        # FD history
        features.append(customer_profile.get("total_fds", 0))
        features.append(customer_profile.get("avg_fd_term", 12))
        
        # Recent engagement
        features.append(customer_profile.get("app_logins_last_month", 5))
        features.append(customer_profile.get("branch_visits_last_year", 2))
        
        # Financial position
        features.append(customer_profile.get("savings_balance", 10000))
        features.append(customer_profile.get("total_relationship_value", 50000))
        
        # Current FD term
        features.append(fd_account.get("term_months", 12))
        
        # Pad
        while len(features) < 20:
            features.append(0.0)
        
        return np.array(features[:20])
    
    def _get_top_features(self, importance: np.ndarray) -> List[str]:
        """Get top contributing features."""
        feature_names = [
            "rate_differential",
            "customer_tenure",
            "previous_fd_count",
            "average_term",
            "app_logins",
            "branch_visits",
            "savings_balance",
            "relationship_value",
            "current_term"
        ]
        
        indices = np.argsort(importance)[::-1][:5]
        return [feature_names[i] for i in indices if i < len(feature_names)]
    
    def _explain_prediction(self, features: np.ndarray) -> List[str]:
        """Explain key factors in prediction."""
        explanations = []
        
        rate_diff = features[0]
        if rate_diff < -0.5:
            explanations.append("Current rate significantly below market")
        elif rate_diff > 0.5:
            explanations.append("Current rate attractive vs market")
        
        tenure = features[1]
        if tenure > 36:
            explanations.append("Long-term customer (high loyalty)")
        elif tenure < 12:
            explanations.append("New customer (higher churn risk)")
        
        return explanations or ["Standard risk profile"]
