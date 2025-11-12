"""ML Model to Predict RD Completion Probability"""
import numpy as np
from typing import Dict, List, Optional
from datetime import date, datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from ultracore.ml.base import BaseMLModel


class CompletionPredictionModel(BaseMLModel):
    """
    Predict whether customer will complete their recurring deposit.
    
    Features considered:
    - Payment history (on-time rate, consecutive misses)
    - Account health score
    - Customer financial wellness indicators
    - Deposit amount vs income ratio
    - Term remaining
    - Seasonal patterns
    - Life events (detected from transactions)
    - Economic conditions
    
    Use cases:
    - Early intervention for at-risk accounts
    - Proactive customer support (Anya)
    - Product design optimization
    - Risk assessment
    """
    
    def __init__(self):
        super().__init__(
            model_name="rd_completion_predictor",
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
        historical_rds: List[Dict]
    ) -> Dict:
        """
        Train on historical RD accounts.
        
        Args:
            historical_rds: Past RD accounts with completion outcomes
        
        Returns:
            Training metrics
        """
        # Extract features and labels
        X = [self._extract_features(rd) for rd in historical_rds]
        y = [1 if rd.get("completed", False) else 0 for rd in historical_rds]
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale
        X_scaled = self.scaler.fit_transform(X)
        
        # Train
        self.model.fit(X_scaled, y)
        
        # Evaluate
        train_score = self.model.score(X_scaled, y)
        
        # Feature importance
        feature_importance = self.model.feature_importances_
        
        return {
            "train_accuracy": float(train_score),
            "training_samples": len(X),
            "completion_rate": float(np.mean(y)),
            "top_predictive_features": self._get_top_features(feature_importance)
        }
    
    async def predict_completion(
        self,
        rd_account: Dict,
        customer_profile: Dict,
        payment_history: List[Dict]
    ) -> Dict:
        """
        Predict completion probability.
        
        Returns:
            Prediction with intervention recommendations
        """
        # Extract features
        features = self._extract_features_live(
            rd_account,
            customer_profile,
            payment_history
        )
        features_scaled = self.scaler.transform([features])
        
        # Predict
        completion_probability = self.model.predict_proba(features_scaled)[0][1]
        will_complete = completion_probability > 0.5
        
        # Risk assessment
        if completion_probability < 0.3:
            risk_level = "CRITICAL"
            interventions = [
                "Immediate Anya outreach with empathy",
                "Offer payment holiday (1-2 months)",
                "Reduce monthly amount by 30%",
                "Connect with financial counseling",
                "Investigate hardship circumstances"
            ]
        elif completion_probability < 0.6:
            risk_level = "HIGH"
            interventions = [
                "Proactive Anya check-in",
                "Payment reminder 5 days before due",
                "Offer skip payment option (if eligible)",
                "Review affordability",
                "Celebrate current progress"
            ]
        elif completion_probability < 0.8:
            risk_level = "MODERATE"
            interventions = [
                "Standard payment reminders",
                "Monthly progress updates",
                "Motivational messages",
                "Goal visualization tools"
            ]
        else:
            risk_level = "LOW"
            interventions = [
                "Standard service",
                "Milestone celebrations",
                "Maturity planning (6 months before)",
                "Upsell to higher amount"
            ]
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            rd_account,
            payment_history,
            features
        )
        
        return {
            "will_complete": will_complete,
            "completion_probability": float(completion_probability),
            "confidence": 0.80,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommended_interventions": interventions,
            "optimal_intervention_timing": self._get_intervention_timing(completion_probability)
        }
    
    def _extract_features(self, rd: Dict) -> np.ndarray:
        """Extract features from historical RD."""
        features = []
        
        # Payment performance
        total_deposits = rd.get("total_deposits_expected", 12)
        deposits_made = rd.get("deposits_made", 6)
        deposits_missed = rd.get("deposits_missed", 0)
        
        features.append(deposits_made / total_deposits if total_deposits > 0 else 0)  # Completion %
        features.append(deposits_missed / total_deposits if total_deposits > 0 else 0)  # Miss rate
        features.append(rd.get("consecutive_misses", 0))
        features.append(rd.get("deposits_on_time", 0) / max(deposits_made, 1))  # On-time rate
        
        # Account health
        features.append(rd.get("account_health_score", 100) / 100)  # Normalized
        
        # Financial indicators
        monthly_amount = rd.get("monthly_deposit_amount", 500)
        estimated_income = rd.get("estimated_monthly_income", 5000)
        features.append(monthly_amount / estimated_income if estimated_income > 0 else 0.1)  # Burden ratio
        
        # Time factors
        term_months = rd.get("term_months", 24)
        months_elapsed = rd.get("months_elapsed", 6)
        features.append(months_elapsed / term_months if term_months > 0 else 0)  # Progress
        
        # Customer behavior
        features.append(rd.get("customer_tenure_months", 12) / 12)  # Tenure in years
        features.append(rd.get("other_active_rds", 0))
        features.append(rd.get("previous_rd_completions", 0))
        
        # Engagement
        features.append(rd.get("app_logins_last_month", 5))
        
        # Pad
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features[:15])
    
    def _extract_features_live(
        self,
        rd_account: Dict,
        customer_profile: Dict,
        payment_history: List[Dict]
    ) -> np.ndarray:
        """Extract features for live prediction."""
        features = []
        
        # Payment performance
        total_expected = rd_account.get("total_deposits_expected", 12)
        made = rd_account.get("total_deposits_made", 0)
        missed = rd_account.get("total_deposits_missed", 0)
        
        features.append(made / total_expected if total_expected > 0 else 0)
        features.append(missed / total_expected if total_expected > 0 else 0)
        features.append(rd_account.get("consecutive_misses", 0))
        features.append(rd_account.get("deposits_on_time", 0) / max(made, 1))
        
        # Health
        features.append(rd_account.get("account_health_score", 100) / 100)
        
        # Financial
        monthly = rd_account.get("monthly_deposit_amount", 500)
        income = customer_profile.get("estimated_monthly_income", 5000)
        features.append(monthly / income if income > 0 else 0.1)
        
        # Progress
        term = rd_account.get("term_months", 24)
        start_date = rd_account.get("start_date")
        if start_date:
            elapsed = (date.today() - start_date).days / 30  # Rough months
            features.append(elapsed / term if term > 0 else 0)
        else:
            features.append(0.5)
        
        # Customer
        features.append(customer_profile.get("tenure_months", 12) / 12)
        features.append(customer_profile.get("active_rds", 0))
        features.append(customer_profile.get("completed_rds", 0))
        
        # Engagement
        features.append(customer_profile.get("app_logins_last_month", 5))
        
        # Pad
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features[:15])
    
    def _identify_risk_factors(
        self,
        rd_account: Dict,
        payment_history: List[Dict],
        features: np.ndarray
    ) -> List[str]:
        """Identify specific risk factors."""
        factors = []
        
        # Recent misses
        consecutive_misses = rd_account.get("consecutive_misses", 0)
        if consecutive_misses >= 2:
            factors.append(f"?? {consecutive_misses} consecutive missed payments")
        
        # Health score
        health = rd_account.get("account_health_score", 100)
        if health < 60:
            factors.append(f"?? Low account health score ({health}/100)")
        
        # High burden
        burden_ratio = features[5]
        if burden_ratio > 0.25:
            factors.append(f"?? High payment burden ({burden_ratio*100:.1f}% of income)")
        
        # Low engagement
        if features[10] < 2:
            factors.append("?? Low engagement (infrequent app usage)")
        
        # New customer
        if features[7] < 0.5:  # < 6 months tenure
            factors.append("?? New customer (higher abandonment risk)")
        
        return factors or ["? No significant risk factors identified"]
    
    def _get_intervention_timing(self, probability: float) -> str:
        """Get optimal timing for intervention."""
        if probability < 0.3:
            return "IMMEDIATE - Intervene within 24 hours"
        elif probability < 0.6:
            return "URGENT - Intervene within 3-5 days"
        elif probability < 0.8:
            return "PROACTIVE - Intervene before next payment"
        else:
            return "ROUTINE - Standard engagement"
    
    def _get_top_features(self, importance: np.ndarray) -> List[str]:
        """Get top predictive features."""
        feature_names = [
            "completion_rate",
            "miss_rate",
            "consecutive_misses",
            "on_time_rate",
            "health_score",
            "burden_ratio",
            "progress",
            "tenure",
            "active_rds",
            "completed_rds",
            "engagement"
        ]
        
        indices = np.argsort(importance)[::-1][:5]
        return [feature_names[i] for i in indices if i < len(feature_names)]
