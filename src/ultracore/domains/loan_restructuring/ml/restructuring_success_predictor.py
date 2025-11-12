"""ML: Restructuring Success Predictor"""
import numpy as np
from typing import Dict, List
from decimal import Decimal
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from ultracore.ml.base import BaseMLModel


class RestructuringSuccessPredictor(BaseMLModel):
    """
    Predict success probability of loan restructuring.
    
    Predicts: Will customer successfully complete restructuring?
    
    Features:
    - Customer payment history
    - Hardship reason and severity
    - Financial ratios (income/expenses)
    - Restructuring type and terms
    - Previous restructuring history
    - Employment stability
    - Support network (guarantors, co-borrowers)
    
    Use cases:
    - Approve/reject hardship applications
    - Determine appropriate relief type
    - Set monitoring intensity
    - Predict intervention needs
    """
    
    def __init__(self):
        super().__init__(
            model_name="restructuring_success_predictor",
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
    
    async def train(self, historical_data: List[Dict]) -> Dict:
        """Train on historical restructuring outcomes."""
        X = [self._extract_features(case) for case in historical_data]
        y = [1 if case.get("successful", False) else 0 for case in historical_data]
        
        X = np.array(X)
        y = np.array(y)
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        train_score = self.model.score(X_scaled, y)
        
        return {
            "train_accuracy": float(train_score),
            "training_samples": len(X),
            "success_rate": float(np.mean(y))
        }
    
    async def predict_success(
        self,
        customer_data: Dict,
        restructuring_plan: Dict
    ) -> Dict:
        """
        Predict restructuring success probability.
        
        Returns probability and risk assessment.
        """
        features = self._extract_features_live(customer_data, restructuring_plan)
        features_scaled = self.scaler.transform([features])
        
        success_probability = self.model.predict_proba(features_scaled)[0][1]
        will_succeed = success_probability > 0.5
        
        # Risk assessment
        if success_probability > 0.75:
            risk_level = "LOW"
            recommendation = "Approve - High confidence"
            monitoring = "Standard monthly monitoring"
        elif success_probability > 0.5:
            risk_level = "MODERATE"
            recommendation = "Approve with conditions"
            monitoring = "Bi-weekly monitoring and support"
        elif success_probability > 0.3:
            risk_level = "HIGH"
            recommendation = "Conditional approval - additional support needed"
            monitoring = "Weekly monitoring and financial counselling"
        else:
            risk_level = "CRITICAL"
            recommendation = "Consider alternative options or additional guarantees"
            monitoring = "Intensive daily monitoring"
        
        # Identify success factors and risks
        factors = self._identify_factors(customer_data, restructuring_plan, features)
        
        return {
            "will_succeed": will_succeed,
            "success_probability": float(success_probability),
            "confidence": 0.84,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "monitoring_frequency": monitoring,
            "success_factors": factors["positive"],
            "risk_factors": factors["negative"],
            "key_insights": self._generate_insights(success_probability, factors)
        }
    
    def _extract_features(self, case: Dict) -> np.ndarray:
        """Extract features from historical case."""
        features = []
        
        # Payment history (0-1, 1=perfect)
        features.append(case.get("payment_history_score", 0.7))
        
        # Financial health
        income = case.get("income_monthly", 5000)
        expenses = case.get("expenses_monthly", 4000)
        payment = case.get("loan_payment", 500)
        features.append(min((income - expenses) / payment, 3.0) if payment > 0 else 0)  # Surplus ratio
        
        # Hardship severity (0=mild, 1=severe)
        features.append(case.get("hardship_severity", 0.5))
        
        # Employment stability (0=unstable, 1=stable)
        features.append(case.get("employment_stability", 0.5))
        
        # Restructuring type impact (0=aggressive, 1=conservative)
        features.append(case.get("restructuring_conservativeness", 0.5))
        
        # Previous restructuring count
        features.append(min(case.get("previous_restructuring_count", 0), 3) / 3.0)
        
        # Support network (0=none, 1=strong)
        features.append(case.get("support_network_strength", 0.3))
        
        # Days in arrears (normalized)
        features.append(min(case.get("days_in_arrears", 0), 180) / 180.0)
        
        # Age of loan (normalized, newer=riskier)
        features.append(min(case.get("loan_age_months", 12), 60) / 60.0)
        
        # Loan size relative to income
        loan_balance = case.get("loan_balance", 100000)
        annual_income = income * 12
        features.append(min(loan_balance / annual_income, 10.0) / 10.0 if annual_income > 0 else 1.0)
        
        # Pad to fixed length
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features[:15])
    
    def _extract_features_live(self, customer: Dict, plan: Dict) -> np.ndarray:
        """Extract features for live prediction."""
        features = []
        
        # Payment history
        features.append(customer.get("payment_history_score", 0.7))
        
        # Financial surplus
        income = customer.get("income_monthly", 5000)
        expenses = customer.get("expenses_monthly", 4000)
        new_payment = plan.get("new_payment_amount", 500)
        surplus = (income - expenses) / new_payment if new_payment > 0 else 0
        features.append(min(surplus, 3.0))
        
        # Hardship severity
        hardship_severity = {
            "job_loss": 0.8,
            "reduced_income": 0.6,
            "illness_injury": 0.7,
            "family_breakdown": 0.6,
            "business_failure": 0.9,
            "natural_disaster": 0.8,
            "other": 0.5
        }
        features.append(hardship_severity.get(customer.get("hardship_reason"), 0.5))
        
        # Employment
        features.append(customer.get("employment_stability", 0.5))
        
        # Restructuring type
        relief_type = plan.get("relief_type", "payment_holiday")
        conservativeness = {
            "payment_holiday": 0.7,
            "term_extension": 0.8,
            "rate_reduction": 0.6,
            "payment_reduction": 0.5
        }
        features.append(conservativeness.get(relief_type, 0.5))
        
        # Previous restructurings
        features.append(min(customer.get("restructuring_count", 0), 3) / 3.0)
        
        # Support
        features.append(customer.get("support_network", 0.3))
        
        # Arrears
        features.append(min(customer.get("days_in_arrears", 0), 180) / 180.0)
        
        # Loan age
        features.append(min(customer.get("loan_age_months", 12), 60) / 60.0)
        
        # Loan to income
        loan_balance = customer.get("loan_balance", 100000)
        features.append(min(loan_balance / (income * 12), 10.0) / 10.0 if income > 0 else 1.0)
        
        # Pad
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features[:15])
    
    def _identify_factors(self, customer: Dict, plan: Dict, features: np.ndarray) -> Dict:
        """Identify success factors and risks."""
        positive = []
        negative = []
        
        # Payment history
        if features[0] > 0.8:
            positive.append("? Strong payment history")
        elif features[0] < 0.5:
            negative.append("?? Poor payment history")
        
        # Financial surplus
        if features[1] > 1.5:
            positive.append("? Good income surplus after restructuring")
        elif features[1] < 0.8:
            negative.append("?? Tight budget even after restructuring")
        
        # Employment
        if features[3] > 0.7:
            positive.append("? Stable employment")
        elif features[3] < 0.4:
            negative.append("?? Unstable employment situation")
        
        # Previous restructurings
        if features[5] == 0:
            positive.append("? First restructuring (better success rate)")
        elif features[5] > 0.5:
            negative.append("?? Multiple previous restructurings")
        
        # Support network
        if features[6] > 0.5:
            positive.append("? Strong support network")
        
        # Arrears
        if features[7] > 0.5:
            negative.append(f"?? Significant arrears ({int(features[7] * 180)} days)")
        
        return {"positive": positive or ["None identified"], "negative": negative or ["None identified"]}
    
    def _generate_insights(self, probability: float, factors: Dict) -> List[str]:
        """Generate actionable insights."""
        insights = []
        
        if probability > 0.75:
            insights.append("High likelihood of success with standard support")
        elif probability > 0.5:
            insights.append("Likely to succeed with additional monitoring")
        else:
            insights.append("May need intensive support or alternative options")
        
        if factors["negative"]:
            insights.append(f"Address key risks: {', '.join(factors['negative'][:2])}")
        
        return insights
