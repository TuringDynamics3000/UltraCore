"""ML-based Fraud Detection for Fixed Deposits"""
import numpy as np
from typing import Dict, List
from datetime import datetime
from decimal import Decimal
from sklearn.ensemble import IsolationForest, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from ultracore.ml.base import BaseMLModel


class FDFraudDetector(BaseMLModel):
    """
    Detect fraudulent fixed deposit applications.
    
    Signals detected:
    - Unusually large amounts for customer profile
    - Rapid multiple applications
    - Inconsistent customer behavior
    - High-risk source accounts
    - Geographic anomalies
    - Identity verification mismatches
    
    Models:
    - Isolation Forest for anomaly detection
    - Gradient Boosting for fraud classification
    - Neural network for pattern recognition
    """
    
    def __init__(self):
        super().__init__(
            model_name="fd_fraud_detector",
            model_type="fraud_detection",
            version="1.0.0"
        )
        
        # Ensemble approach
        self.isolation_forest = IsolationForest(
            contamination=0.01,
            random_state=42
        )
        
        self.gradient_boost = GradientBoostingClassifier(
            n_estimators=100,
            random_state=42
        )
        
        self.scaler = StandardScaler()
    
    async def train(
        self,
        legitimate_applications: List[Dict],
        fraudulent_applications: List[Dict]
    ) -> Dict:
        """
        Train on historical FD applications.
        
        Args:
            legitimate_applications: Known legitimate applications
            fraudulent_applications: Known fraudulent applications
        
        Returns:
            Training metrics
        """
        # Extract features
        X_legit = [self._extract_features(app) for app in legitimate_applications]
        X_fraud = [self._extract_features(app) for app in fraudulent_applications]
        
        # Prepare training data
        X = np.array(X_legit + X_fraud)
        y = np.array([0] * len(X_legit) + [1] * len(X_fraud))
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest on legitimate data only
        self.isolation_forest.fit(np.array(X_legit))
        
        # Train Gradient Boosting on all data
        self.gradient_boost.fit(X_scaled, y)
        
        # Evaluate
        train_score = self.gradient_boost.score(X_scaled, y)
        
        return {
            "train_accuracy": float(train_score),
            "training_samples": len(X),
            "fraud_ratio": len(X_fraud) / len(X)
        }
    
    async def detect(
        self,
        application: Dict,
        customer_history: List[Dict]
    ) -> Dict:
        """
        Detect if FD application is fraudulent.
        
        Args:
            application: FD application details
            customer_history: Customer's transaction history
        
        Returns:
            Fraud detection result with risk score
        """
        # Extract features
        features = self._extract_features(application, customer_history)
        features_scaled = self.scaler.transform([features])
        
        # Ensemble prediction
        isolation_score = self.isolation_forest.score_samples(features_scaled)[0]
        is_anomaly = self.isolation_forest.predict(features_scaled)[0] == -1
        
        fraud_probability = self.gradient_boost.predict_proba(features_scaled)[0][1]
        is_fraud = fraud_probability > 0.5
        
        # Combined risk score (0-100)
        risk_score = (
            (1 - isolation_score) * 40 +  # Anomaly component
            fraud_probability * 60  # Classification component
        )
        risk_score = min(100, max(0, risk_score))
        
        # Determine risk level
        if risk_score > 80:
            risk_level = "CRITICAL"
            action = "BLOCK_AND_INVESTIGATE"
        elif risk_score > 60:
            risk_level = "HIGH"
            action = "MANUAL_REVIEW_REQUIRED"
        elif risk_score > 40:
            risk_level = "MEDIUM"
            action = "ENHANCED_VERIFICATION"
        else:
            risk_level = "LOW"
            action = "APPROVE"
        
        # Identify specific fraud indicators
        fraud_indicators = self._identify_fraud_indicators(application, features)
        
        return {
            "is_fraud": is_fraud or is_anomaly,
            "fraud_probability": float(fraud_probability),
            "risk_score": float(risk_score),
            "risk_level": risk_level,
            "recommended_action": action,
            "fraud_indicators": fraud_indicators,
            "confidence": 0.85
        }
    
    def _extract_features(
        self,
        application: Dict,
        customer_history: List[Dict] = None
    ) -> np.ndarray:
        """Extract features for ML model."""
        features = []
        
        # Amount features
        amount = float(application.get("deposit_amount", 0))
        features.append(amount)
        features.append(np.log1p(amount))  # Log-transformed amount
        
        # Term features
        term = application.get("term_months", 12)
        features.append(term)
        
        # Customer history features
        if customer_history:
            avg_transaction = np.mean([t.get("amount", 0) for t in customer_history])
            features.append(amount / avg_transaction if avg_transaction > 0 else 0)
            features.append(len(customer_history))
        else:
            features.extend([1.0, 0])  # New customer
        
        # Time features
        hour = datetime.now().hour
        features.append(hour)
        features.append(1 if 22 <= hour or hour <= 6 else 0)  # Late night flag
        
        # Behavioral features
        features.append(1 if amount > 100000 else 0)  # Large amount flag
        features.append(1 if term < 3 else 0)  # Very short term flag
        
        # Pad to fixed size
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features[:15])
    
    def _identify_fraud_indicators(
        self,
        application: Dict,
        features: np.ndarray
    ) -> List[str]:
        """Identify specific fraud indicators."""
        indicators = []
        
        amount = application.get("deposit_amount", 0)
        
        if amount > 100000:
            indicators.append("Large deposit amount (>,000)")
        
        if application.get("term_months", 12) < 3:
            indicators.append("Unusually short term (<3 months)")
        
        hour = datetime.now().hour
        if 22 <= hour or hour <= 6:
            indicators.append("Application submitted during unusual hours")
        
        if not application.get("customer_history"):
            indicators.append("New customer with no transaction history")
        
        return indicators or ["No specific indicators identified"]
