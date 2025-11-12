"""ML: Spending Pattern Analysis"""
import numpy as np
from typing import Dict, List
from decimal import Decimal
from sklearn.cluster import KMeans

from ultracore.ml.base import BaseMLModel


class SpendingAnalyzer(BaseMLModel):
    """
    Analyze customer spending patterns.
    
    Features:
    - Category classification (groceries, transport, etc.)
    - Spending forecasting
    - Unusual spending detection
    - Financial wellness insights
    
    Use cases:
    - Budgeting assistance
    - Savings recommendations
    - Fraud detection support
    - Product recommendations
    """
    
    def __init__(self):
        super().__init__(
            model_name="spending_analyzer",
            model_type="clustering",
            version="1.0.0"
        )
        
        self.model = KMeans(n_clusters=8, random_state=42)
    
    async def analyze_spending(
        self,
        transactions: List[Dict]
    ) -> Dict:
        """
        Analyze spending patterns.
        
        Returns insights and recommendations.
        """
        
        # Category spending
        category_totals = {}
        for txn in transactions:
            cat = txn.get("category", "other")
            amt = txn.get("amount", 0)
            category_totals[cat] = category_totals.get(cat, 0) + amt
        
        total_spending = sum(category_totals.values())
        
        # Top categories
        sorted_cats = sorted(
            category_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        insights = []
        
        # Insights
        if category_totals.get("groceries", 0) / total_spending > 0.3:
            insights.append("Groceries are your biggest expense (30%+)")
        
        if category_totals.get("entertainment", 0) / total_spending > 0.15:
            insights.append("High entertainment spending - consider reducing")
        
        return {
            "total_spending": float(total_spending),
            "category_breakdown": category_totals,
            "top_categories": sorted_cats[:5],
            "insights": insights,
            "savings_opportunities": self._identify_savings(category_totals)
        }
    
    def _identify_savings(self, categories: Dict) -> List[str]:
        """Identify savings opportunities."""
        opportunities = []
        
        if categories.get("dining", 0) > 500:
            opportunities.append("Reduce dining out by $100/month = $1,200/year saved")
        
        if categories.get("subscriptions", 0) > 100:
            opportunities.append("Review subscriptions - cancel unused ones")
        
        return opportunities
