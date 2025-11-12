"""ML Model to Predict LVR Breach Risk"""
import numpy as np
from typing import Dict, List, Optional
from decimal import Decimal
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from ultracore.ml.base import BaseMLModel


class LVRBreachPredictor(BaseMLModel):
    """
    Predict risk of LVR breach in next 6-12 months.
    
    Features considered:
    - Current LVR and trend
    - Property market conditions
    - Property type and location
    - Loan payment history
    - Economic indicators
    - Property age and condition
    - Local market volatility
    
    Use cases:
    - Proactive monitoring
    - Early intervention
    - Additional security decisions
    - Portfolio risk assessment
    """
    
    def __init__(self):
        super().__init__(
            model_name="lvr_breach_predictor",
            model_type="classification",
            version="1.0.0"
        )
        
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.scaler = StandardScaler()
    
    async def train(
        self,
        historical_collateral: List[Dict]
    ) -> Dict:
        """
        Train on historical collateral with known LVR outcomes.
        """
        X = [self._extract_features(col) for col in historical_collateral]
        y = [1 if col.get("lvr_breach_occurred", False) else 0 for col in historical_collateral]
        
        X = np.array(X)
        y = np.array(y)
        
        X_scaled = self.scaler.fit_transform(X)
        
        self.model.fit(X_scaled, y)
        
        train_score = self.model.score(X_scaled, y)
        
        feature_importance = self.model.feature_importances_
        
        return {
            "train_accuracy": float(train_score),
            "training_samples": len(X),
            "breach_rate": float(np.mean(y)),
            "top_predictive_features": self._get_top_features(feature_importance)
        }
    
    async def predict_lvr_breach(
        self,
        collateral: Dict,
        loan: Dict,
        market_conditions: Dict
    ) -> Dict:
        """
        Predict LVR breach probability in next 6-12 months.
        """
        features = self._extract_features_live(collateral, loan, market_conditions)
        features_scaled = self.scaler.transform([features])
        
        breach_probability = self.model.predict_proba(features_scaled)[0][1]
        will_breach = breach_probability > 0.5
        
        # Risk assessment
        if breach_probability > 0.7:
            risk_level = "CRITICAL"
            actions = [
                "Order immediate professional valuation",
                "Contact borrower proactively",
                "Request additional security",
                "Consider loan restructure",
                "Increase monitoring frequency"
            ]
        elif breach_probability > 0.5:
            risk_level = "HIGH"
            actions = [
                "Schedule valuation in 30 days",
                "Monitor market closely",
                "Prepare borrower communication",
                "Review additional security options"
            ]
        elif breach_probability > 0.3:
            risk_level = "MODERATE"
            actions = [
                "Continue standard monitoring",
                "Schedule valuation in 90 days",
                "Track market trends"
            ]
        else:
            risk_level = "LOW"
            actions = [
                "Standard annual valuation",
                "Routine monitoring"
            ]
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            collateral,
            loan,
            market_conditions,
            features
        )
        
        return {
            "will_breach": will_breach,
            "breach_probability": float(breach_probability),
            "confidence": 0.82,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommended_actions": actions,
            "monitoring_frequency": self._get_monitoring_frequency(breach_probability),
            "estimated_time_to_breach": self._estimate_time_to_breach(breach_probability, features)
        }
    
    def _extract_features(self, col: Dict) -> np.ndarray:
        """Extract features from historical collateral."""
        features = []
        
        # Current LVR
        features.append(col.get("current_lvr", 75) / 100)
        
        # LVR trend (change over last 6 months)
        features.append(col.get("lvr_change_6m", 0) / 100)
        
        # Property market condition
        market_change = col.get("market_value_change_12m", 0)  # -10 to +20
        features.append(market_change / 100)
        
        # Property age
        features.append(min(col.get("property_age_years", 10), 100) / 100)
        
        # Location risk (0=CBD, 1=regional, 0.5=suburban)
        features.append(col.get("location_risk", 0.3))
        
        # Payment history (0-1, 1=perfect)
        features.append(col.get("payment_history_score", 0.95))
        
        # Economic indicators
        features.append(col.get("unemployment_rate", 5) / 20)  # Normalize to 0-1
        features.append(col.get("interest_rate", 5) / 10)
        
        # Property type risk (house=0.2, unit=0.5, land=0.8)
        features.append(col.get("property_type_risk", 0.3))
        
        # Market volatility
        features.append(col.get("market_volatility", 0.1))
        
        # Pad to fixed length
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features[:15])
    
    def _extract_features_live(
        self,
        collateral: Dict,
        loan: Dict,
        market: Dict
    ) -> np.ndarray:
        """Extract features for live prediction."""
        features = []
        
        # Current LVR
        current_lvr = collateral.get("current_lvr", 75)
        features.append(current_lvr / 100)
        
        # LVR trend
        lvr_6m_ago = collateral.get("lvr_6_months_ago", current_lvr - 2)
        features.append((current_lvr - lvr_6m_ago) / 100)
        
        # Market change
        features.append(market.get("value_change_12m", 5) / 100)
        
        # Property age
        features.append(min(collateral.get("property_age", 10), 100) / 100)
        
        # Location risk
        location_type = collateral.get("location_type", "suburban")
        location_risk = {"cbd": 0.2, "suburban": 0.3, "regional": 0.6}.get(location_type, 0.3)
        features.append(location_risk)
        
        # Payment history
        features.append(loan.get("payment_history_score", 0.95))
        
        # Economic
        features.append(market.get("unemployment_rate", 5) / 20)
        features.append(market.get("interest_rate", 5) / 10)
        
        # Property type
        prop_type = collateral.get("property_type", "house")
        type_risk = {"house": 0.2, "unit": 0.5, "land": 0.8}.get(prop_type, 0.3)
        features.append(type_risk)
        
        # Volatility
        features.append(market.get("volatility", 0.1))
        
        # Pad
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features[:15])
    
    def _identify_risk_factors(
        self,
        collateral: Dict,
        loan: Dict,
        market: Dict,
        features: np.ndarray
    ) -> List[str]:
        """Identify specific risk factors."""
        factors = []
        
        # High LVR
        current_lvr = collateral.get("current_lvr", 75)
        if current_lvr > 75:
            factors.append(f"?? High LVR ({current_lvr:.1f}%)")
        
        # Rising LVR
        if features[1] > 0.05:  # 5%+ increase
            factors.append("?? LVR trending upward")
        
        # Declining market
        if features[2] < -0.05:  # 5%+ decline
            factors.append(f"?? Property market declining ({features[2]*100:.1f}%)")
        
        # Payment issues
        if loan.get("payment_history_score", 1.0) < 0.9:
            factors.append("?? Payment history concerns")
        
        # High volatility market
        if market.get("volatility", 0) > 0.2:
            factors.append("?? High market volatility")
        
        # Regional property
        if collateral.get("location_type") == "regional":
            factors.append("?? Regional property (higher risk)")
        
        return factors or ["? No significant risk factors identified"]
    
    def _get_monitoring_frequency(self, probability: float) -> str:
        """Get recommended monitoring frequency."""
        if probability > 0.7:
            return "DAILY - Critical risk"
        elif probability > 0.5:
            return "WEEKLY - High risk"
        elif probability > 0.3:
            return "MONTHLY - Moderate risk"
        else:
            return "QUARTERLY - Low risk"
    
    def _estimate_time_to_breach(self, probability: float, features: np.ndarray) -> str:
        """Estimate time until likely breach."""
        if probability < 0.3:
            return ">12 months (if at all)"
        elif probability < 0.5:
            return "9-12 months"
        elif probability < 0.7:
            return "6-9 months"
        else:
            return "3-6 months"
    
    def _get_top_features(self, importance: np.ndarray) -> List[str]:
        """Get top predictive features."""
        feature_names = [
            "current_lvr",
            "lvr_trend",
            "market_change",
            "property_age",
            "location_risk",
            "payment_history",
            "unemployment",
            "interest_rate",
            "property_type",
            "volatility"
        ]
        
        indices = np.argsort(importance)[::-1][:5]
        return [feature_names[i] for i in indices if i < len(feature_names)]
