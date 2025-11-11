"""
UltraCore Account Management - ML Models

Machine learning models for:
- Balance prediction (LSTM, Prophet)
- Transaction categorization (NLP)
- Churn prediction (XGBoost)
- Anomaly detection (Isolation Forest)
- Customer lifetime value (LTV)
- Interest rate optimization (Reinforcement Learning)
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
import uuid
import numpy as np
from collections import defaultdict

from ultracore.accounts.core.account_models import (
    Account, Transaction, TransactionType
)


# ============================================================================
# ML Model Results
# ============================================================================

@dataclass
class BalancePrediction:
    """Balance prediction result"""
    account_id: str
    prediction_date: date
    predicted_balance: Decimal
    confidence_interval_lower: Decimal
    confidence_interval_upper: Decimal
    confidence: Decimal  # 0-1
    model_used: str
    features_used: List[str] = field(default_factory=list)
    predicted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TransactionCategory:
    """Transaction categorization result"""
    transaction_id: str
    category: str
    subcategory: Optional[str] = None
    confidence: Decimal = Decimal('0.0')
    model_version: str = "v1.0"
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChurnPrediction:
    """Customer churn prediction"""
    customer_id: str
    account_id: str
    churn_probability: Decimal  # 0-1
    churn_risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    contributing_factors: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    prediction_date: date = field(default_factory=date.today)
    valid_until: date = field(default_factory=lambda: date.today() + timedelta(days=30))


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    transaction_id: str
    is_anomaly: bool
    anomaly_score: Decimal  # 0-1 (higher = more anomalous)
    anomaly_type: Optional[str] = None
    features_contributing: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class LifetimeValuePrediction:
    """Customer lifetime value prediction"""
    customer_id: str
    predicted_ltv: Decimal
    time_horizon_months: int = 36
    confidence_interval: Tuple[Decimal, Decimal] = (Decimal('0'), Decimal('0'))
    revenue_breakdown: Dict[str, Decimal] = field(default_factory=dict)


# ============================================================================
# Balance Prediction Model
# ============================================================================

class BalancePredictionModel:
    """
    Balance prediction using time series models
    
    Models:
    - LSTM (Long Short-Term Memory) - Deep learning
    - Prophet (Facebook's time series) - Statistical
    - ARIMA (AutoRegressive Integrated Moving Average) - Statistical
    
    Features:
    - Historical balances
    - Transaction patterns
    - Day of week/month effects
    - Seasonality
    """
    
    def __init__(self):
        self.model_name = "BalancePredictionLSTM"
        self.version = "v1.0"
        self.trained = False
        
        # Simulated model weights (in production: actual LSTM/Prophet model)
        self.weights = None
    
    async def predict_balance(
        self,
        account: Account,
        prediction_days: int = 30
    ) -> List[BalancePrediction]:
        """
        Predict future balances
        
        Process:
        1. Extract features from account history
        2. Apply time series model
        3. Generate predictions with confidence intervals
        """
        
        predictions = []
        
        # Get current balance
        current_balance = account.balance.ledger_balance
        
        # Extract features
        features = self._extract_balance_features(account)
        
        # Simulate predictions (in production: use actual LSTM/Prophet)
        for days_ahead in range(1, prediction_days + 1):
            prediction_date = date.today() + timedelta(days=days_ahead)
            
            # Simple trend-based prediction (replace with actual model)
            trend = features.get('daily_avg_change', Decimal('0.0'))
            volatility = features.get('balance_volatility', Decimal('100.0'))
            
            predicted_balance = current_balance + (trend * days_ahead)
            
            # Confidence intervals (wider as we go further out)
            uncertainty = volatility * Decimal(str(days_ahead)) * Decimal('0.1')
            lower = predicted_balance - uncertainty
            upper = predicted_balance + uncertainty
            
            # Confidence decreases with time
            confidence = Decimal('0.95') - (Decimal(str(days_ahead)) / Decimal('100'))
            confidence = max(confidence, Decimal('0.5'))
            
            prediction = BalancePrediction(
                account_id=account.account_id,
                prediction_date=prediction_date,
                predicted_balance=predicted_balance,
                confidence_interval_lower=lower,
                confidence_interval_upper=upper,
                confidence=confidence,
                model_used=self.model_name,
                features_used=list(features.keys())
            )
            
            predictions.append(prediction)
        
        # Store predictions on account
        if predictions:
            account.predicted_balance_30d = predictions[29].predicted_balance if len(predictions) >= 30 else predictions[-1].predicted_balance
        
        return predictions
    
    def _extract_balance_features(self, account: Account) -> Dict[str, Any]:
        """Extract features for balance prediction"""
        
        # In production: extract from transaction history
        features = {
            'current_balance': account.balance.ledger_balance,
            'avg_balance_30d': account.balance.ledger_balance,
            'avg_balance_90d': account.balance.ledger_balance,
            'balance_volatility': Decimal('100.0'),
            'daily_avg_change': Decimal('10.0'),
            'deposit_frequency': 15,  # days between deposits
            'withdrawal_frequency': 7,  # days between withdrawals
            'avg_deposit_amount': Decimal('500.0'),
            'avg_withdrawal_amount': Decimal('200.0'),
            'account_age_days': account.get_account_age_days(),
            'has_recurring_deposits': True,
            'has_recurring_withdrawals': True
        }
        
        return features
    
    async def train(self, training_data: List[Dict[str, Any]]):
        """Train the model on historical data"""
        # In production: implement actual LSTM/Prophet training
        self.trained = True


# ============================================================================
# Transaction Categorization Model
# ============================================================================

class TransactionCategorizationModel:
    """
    Transaction categorization using NLP
    
    Techniques:
    - TF-IDF vectorization
    - Merchant name matching
    - Pattern recognition
    - Deep learning (BERT for complex cases)
    
    Categories:
    - Income (Salary, Freelance, Investment)
    - Shopping (Groceries, Clothing, Electronics)
    - Bills (Utilities, Internet, Phone)
    - Transport (Fuel, Public Transport, Ride Share)
    - Food & Dining (Restaurants, Cafes, Delivery)
    - Entertainment (Streaming, Movies, Events)
    - Healthcare (Doctor, Pharmacy, Insurance)
    - Education (Tuition, Books, Courses)
    - Travel (Flights, Hotels, Activities)
    - Other
    """
    
    def __init__(self):
        self.model_name = "TransactionCategorizerNLP"
        self.version = "v1.0"
        
        # Merchant patterns (simplified - in production: use ML model)
        self.patterns = {
            'GROCERIES': ['woolworths', 'coles', 'aldi', 'iga', 'supermarket'],
            'FUEL': ['bp', 'shell', 'caltex', '7-eleven', 'united petroleum'],
            'RESTAURANTS': ['restaurant', 'cafe', 'mcdonald', 'kfc', 'subway'],
            'UTILITIES': ['agl', 'origin', 'energy australia', 'telstra', 'optus'],
            'TRANSPORT': ['uber', 'ola', 'didi', 'taxi'],
            'ENTERTAINMENT': ['netflix', 'spotify', 'disney', 'cinema', 'event'],
            'HEALTHCARE': ['pharmacy', 'chemist', 'doctor', 'medical', 'hospital'],
            'SHOPPING': ['amazon', 'ebay', 'jb hi-fi', 'kmart', 'target'],
            'SALARY': ['salary', 'wages', 'payroll', 'income'],
            'BILLS': ['bill payment', 'direct debit', 'bpay']
        }
    
    async def categorize_transaction(
        self,
        transaction: Transaction
    ) -> TransactionCategory:
        """
        Categorize transaction using NLP
        
        Features:
        - Merchant name
        - Description
        - Amount patterns
        - Transaction type
        - Time of day
        - Historical patterns
        """
        
        # Extract features
        description = transaction.description.lower()
        merchant = (transaction.merchant_name or '').lower()
        amount = transaction.amount
        
        # Try to match patterns
        category = "OTHER"
        confidence = Decimal('0.5')
        subcategory = None
        
        for cat, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern in description or pattern in merchant:
                    category = cat
                    confidence = Decimal('0.85')
                    break
            if category != "OTHER":
                break
        
        # Income detection
        if transaction.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER_IN]:
            if amount > Decimal('1000'):
                category = "INCOME"
                subcategory = "SALARY"
                confidence = Decimal('0.75')
        
        result = TransactionCategory(
            transaction_id=transaction.transaction_id,
            category=category,
            subcategory=subcategory,
            confidence=confidence,
            model_version=self.version,
            features={
                'description': transaction.description,
                'merchant': transaction.merchant_name,
                'amount': str(amount),
                'type': transaction.transaction_type.value
            }
        )
        
        # Store on transaction
        transaction.ml_category = category
        
        return result
    
    async def batch_categorize(
        self,
        transactions: List[Transaction]
    ) -> List[TransactionCategory]:
        """Batch categorize multiple transactions"""
        
        results = []
        for txn in transactions:
            category = await self.categorize_transaction(txn)
            results.append(category)
        
        return results


# ============================================================================
# Churn Prediction Model
# ============================================================================

class ChurnPredictionModel:
    """
    Customer churn prediction using XGBoost
    
    Features:
    - Account activity (transaction frequency, recency)
    - Balance trends (declining, volatile)
    - Product usage (number of products)
    - Service interactions (complaints, support tickets)
    - Demographics
    - Competitive actions
    
    Churn indicators:
    - Declining balance
    - Reduced transaction frequency
    - Closed linked accounts
    - Negative service interactions
    - Rate shopping (competitor checks)
    """
    
    def __init__(self):
        self.model_name = "ChurnPredictorXGBoost"
        self.version = "v1.0"
        
        # Risk thresholds
        self.risk_thresholds = {
            'LOW': Decimal('0.2'),
            'MEDIUM': Decimal('0.4'),
            'HIGH': Decimal('0.6'),
            'CRITICAL': Decimal('0.8')
        }
    
    async def predict_churn(
        self,
        account: Account,
        customer_data: Optional[Dict[str, Any]] = None
    ) -> ChurnPrediction:
        """
        Predict customer churn probability
        
        Process:
        1. Extract features
        2. Apply XGBoost model
        3. Calculate churn probability
        4. Identify contributing factors
        5. Recommend retention actions
        """
        
        # Extract features
        features = self._extract_churn_features(account, customer_data)
        
        # Calculate churn probability (simplified - in production: use XGBoost)
        churn_score = Decimal('0.0')
        contributing_factors = []
        
        # Factor 1: Account activity
        if features['days_since_last_transaction'] > 30:
            churn_score += Decimal('0.2')
            contributing_factors.append({
                'factor': 'Low activity',
                'impact': 0.2,
                'description': f"No transactions in {features['days_since_last_transaction']} days"
            })
        
        # Factor 2: Balance trend
        if features['balance_trend'] == 'DECLINING':
            churn_score += Decimal('0.25')
            contributing_factors.append({
                'factor': 'Declining balance',
                'impact': 0.25,
                'description': 'Balance has been declining consistently'
            })
        
        # Factor 3: Product usage
        if features['product_count'] == 1:
            churn_score += Decimal('0.15')
            contributing_factors.append({
                'factor': 'Single product',
                'impact': 0.15,
                'description': 'Customer has only one product'
            })
        
        # Factor 4: Service interactions
        if features.get('recent_complaints', 0) > 0:
            churn_score += Decimal('0.2')
            contributing_factors.append({
                'factor': 'Service issues',
                'impact': 0.2,
                'description': f"{features['recent_complaints']} recent complaints"
            })
        
        # Cap at 1.0
        churn_probability = min(churn_score, Decimal('1.0'))
        
        # Determine risk level
        risk_level = self._determine_risk_level(churn_probability)
        
        # Recommend actions
        recommended_actions = self._recommend_retention_actions(
            churn_probability,
            contributing_factors
        )
        
        prediction = ChurnPrediction(
            customer_id=account.customer_id,
            account_id=account.account_id,
            churn_probability=churn_probability,
            churn_risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommended_actions=recommended_actions
        )
        
        # Store on account
        account.churn_probability = churn_probability
        
        return prediction
    
    def _extract_churn_features(
        self,
        account: Account,
        customer_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract features for churn prediction"""
        
        days_inactive = account.days_inactive
        
        # Determine balance trend
        balance_trend = "STABLE"
        if account.balance.ledger_balance < account.balance.minimum_balance:
            balance_trend = "DECLINING"
        
        features = {
            'account_age_days': account.get_account_age_days(),
            'days_since_last_transaction': days_inactive,
            'current_balance': account.balance.ledger_balance,
            'balance_trend': balance_trend,
            'transaction_count_30d': 0,  # In production: calculate from history
            'transaction_count_90d': 0,
            'avg_monthly_balance': account.balance.ledger_balance,
            'product_count': 1,  # Simplified
            'has_linked_accounts': len(account.linked_loan_ids) > 0,
            'account_status': account.account_status.value,
            'recent_complaints': 0,
            'service_calls_30d': 0
        }
        
        if customer_data:
            features.update(customer_data)
        
        return features
    
    def _determine_risk_level(self, churn_probability: Decimal) -> str:
        """Determine risk level from probability"""
        
        if churn_probability >= self.risk_thresholds['CRITICAL']:
            return 'CRITICAL'
        elif churn_probability >= self.risk_thresholds['HIGH']:
            return 'HIGH'
        elif churn_probability >= self.risk_thresholds['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _recommend_retention_actions(
        self,
        churn_probability: Decimal,
        factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Recommend retention actions"""
        
        actions = []
        
        if churn_probability >= Decimal('0.6'):
            actions.append("URGENT: Schedule personal outreach call")
            actions.append("Offer retention bonus or rate increase")
        
        if churn_probability >= Decimal('0.4'):
            actions.append("Send personalized retention email")
            actions.append("Offer product bundle upgrade")
        
        # Factor-specific actions
        for factor in factors:
            if factor['factor'] == 'Low activity':
                actions.append("Re-engage: Send account usage tips")
            elif factor['factor'] == 'Service issues':
                actions.append("Service recovery: Personal apology + compensation")
            elif factor['factor'] == 'Single product':
                actions.append("Cross-sell: Recommend additional products")
        
        return actions


# ============================================================================
# Anomaly Detection Model
# ============================================================================

class AnomalyDetectionModel:
    """
    Transaction anomaly detection using Isolation Forest
    
    Detects:
    - Unusual transaction amounts
    - Unexpected merchants
    - Abnormal transaction times
    - Geographic anomalies
    - Velocity anomalies
    
    Used for fraud detection and customer protection
    """
    
    def __init__(self):
        self.model_name = "AnomalyDetectorIsolationForest"
        self.version = "v1.0"
        
        # Anomaly thresholds
        self.anomaly_threshold = Decimal('0.7')  # Score > 0.7 = anomaly
    
    async def detect_anomaly(
        self,
        transaction: Transaction,
        account: Account,
        historical_transactions: List[Transaction]
    ) -> AnomalyDetection:
        """
        Detect if transaction is anomalous
        
        Features:
        - Amount (Z-score)
        - Time of day
        - Day of week
        - Merchant category
        - Geographic location
        - Transaction velocity
        """
        
        # Extract features
        features = self._extract_anomaly_features(
            transaction,
            account,
            historical_transactions
        )
        
        # Calculate anomaly score (simplified - in production: use Isolation Forest)
        anomaly_score = Decimal('0.0')
        contributing_features = []
        
        # Check amount anomaly
        if features['amount_zscore'] > 3:
            anomaly_score += Decimal('0.4')
            contributing_features.append('unusual_amount')
        
        # Check time anomaly
        if features['is_unusual_time']:
            anomaly_score += Decimal('0.2')
            contributing_features.append('unusual_time')
        
        # Check velocity anomaly
        if features['transactions_last_hour'] > 5:
            anomaly_score += Decimal('0.3')
            contributing_features.append('high_velocity')
        
        # Check merchant anomaly
        if features['is_new_merchant']:
            anomaly_score += Decimal('0.1')
            contributing_features.append('new_merchant')
        
        is_anomaly = anomaly_score >= self.anomaly_threshold
        
        # Determine anomaly type
        anomaly_type = None
        explanation = ""
        
        if is_anomaly:
            if 'unusual_amount' in contributing_features:
                anomaly_type = "AMOUNT_ANOMALY"
                explanation = "Transaction amount significantly higher than usual"
            elif 'high_velocity' in contributing_features:
                anomaly_type = "VELOCITY_ANOMALY"
                explanation = "Unusually high transaction frequency"
            else:
                anomaly_type = "PATTERN_ANOMALY"
                explanation = "Transaction pattern differs from normal behavior"
        
        result = AnomalyDetection(
            transaction_id=transaction.transaction_id,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            anomaly_type=anomaly_type,
            features_contributing=contributing_features,
            explanation=explanation
        )
        
        # Store on transaction
        transaction.fraud_score = anomaly_score
        
        return result
    
    def _extract_anomaly_features(
        self,
        transaction: Transaction,
        account: Account,
        historical: List[Transaction]
    ) -> Dict[str, Any]:
        """Extract features for anomaly detection"""
        
        # Calculate statistics from historical transactions
        if historical:
            amounts = [float(t.amount) for t in historical]
            avg_amount = np.mean(amounts)
            std_amount = np.std(amounts)
            
            # Z-score for current transaction
            if std_amount > 0:
                amount_zscore = (float(transaction.amount) - avg_amount) / std_amount
            else:
                amount_zscore = 0
        else:
            amount_zscore = 0
        
        # Check transaction time
        hour = transaction.transaction_date.hour
        is_unusual_time = hour < 6 or hour > 22  # Late night/early morning
        
        # Check velocity (simplified)
        transactions_last_hour = 0  # In production: count from history
        
        # Check merchant
        is_new_merchant = transaction.merchant_name and transaction.merchant_name not in [
            t.merchant_name for t in historical if t.merchant_name
        ]
        
        features = {
            'amount': transaction.amount,
            'amount_zscore': amount_zscore,
            'hour_of_day': hour,
            'is_unusual_time': is_unusual_time,
            'transactions_last_hour': transactions_last_hour,
            'is_new_merchant': is_new_merchant,
            'merchant_category': transaction.merchant_category or 'UNKNOWN'
        }
        
        return features


# ============================================================================
# Lifetime Value Model
# ============================================================================

class LifetimeValueModel:
    """
    Customer lifetime value prediction
    
    Predicts:
    - Future revenue from customer
    - Product cross-sell opportunities
    - Retention probability
    - Profitability
    """
    
    def __init__(self):
        self.model_name = "LTVPredictor"
        self.version = "v1.0"
    
    async def predict_ltv(
        self,
        account: Account,
        time_horizon_months: int = 36
    ) -> LifetimeValuePrediction:
        """Predict customer lifetime value"""
        
        # Simplified LTV calculation (in production: use ML model)
        
        # Interest income (if savings account)
        interest_income = Decimal('0.0')
        if account.interest_bearing and account.current_interest_rate:
            annual_rate = account.current_interest_rate.annual_rate / Decimal('100')
            interest_income = account.balance.ledger_balance * annual_rate * Decimal(str(time_horizon_months)) / Decimal('12')
        
        # Fee income
        monthly_fees = sum(
            fee.amount for fee in account.fee_structure
            if fee.active and fee.frequency == 'MONTHLY'
        )
        fee_income = monthly_fees * time_horizon_months
        
        # Cross-sell opportunities (estimated)
        cross_sell_income = Decimal('500.0')  # Estimated
        
        # Total LTV
        predicted_ltv = interest_income + fee_income + cross_sell_income
        
        # Confidence interval (± 20%)
        lower_bound = predicted_ltv * Decimal('0.8')
        upper_bound = predicted_ltv * Decimal('1.2')
        
        prediction = LifetimeValuePrediction(
            customer_id=account.customer_id,
            predicted_ltv=predicted_ltv,
            time_horizon_months=time_horizon_months,
            confidence_interval=(lower_bound, upper_bound),
            revenue_breakdown={
                'interest_income': interest_income,
                'fee_income': fee_income,
                'cross_sell': cross_sell_income
            }
        )
        
        # Store on account
        account.lifetime_value = predicted_ltv
        
        return prediction


# ============================================================================
# ML Model Manager
# ============================================================================

class MLModelManager:
    """Central manager for all ML models"""
    
    def __init__(self):
        self.balance_predictor = BalancePredictionModel()
        self.transaction_categorizer = TransactionCategorizationModel()
        self.churn_predictor = ChurnPredictionModel()
        self.anomaly_detector = AnomalyDetectionModel()
        self.ltv_predictor = LifetimeValueModel()
    
    async def run_all_models(
        self,
        account: Account,
        transactions: List[Transaction]
    ) -> Dict[str, Any]:
        """Run all ML models on account"""
        
        results = {}
        
        # Balance prediction
        results['balance_predictions'] = await self.balance_predictor.predict_balance(account)
        
        # Transaction categorization
        if transactions:
            results['transaction_categories'] = await self.transaction_categorizer.batch_categorize(transactions)
        
        # Churn prediction
        results['churn_prediction'] = await self.churn_predictor.predict_churn(account)
        
        # Lifetime value
        results['ltv_prediction'] = await self.ltv_predictor.predict_ltv(account)
        
        # Anomaly detection (on recent transactions)
        if transactions:
            recent_txn = transactions[-1]
            historical = transactions[:-1]
            results['anomaly_detection'] = await self.anomaly_detector.detect_anomaly(
                recent_txn,
                account,
                historical
            )
        
        return results


# ============================================================================
# Global Singleton
# ============================================================================

_ml_model_manager: Optional[MLModelManager] = None

def get_ml_model_manager() -> MLModelManager:
    """Get singleton ML model manager"""
    global _ml_model_manager
    if _ml_model_manager is None:
        _ml_model_manager = MLModelManager()
    return _ml_model_manager
