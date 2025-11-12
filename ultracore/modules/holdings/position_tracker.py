"""
Position Tracking with Advanced Cost Basis Methods
Supports multiple cost basis calculation methods for tax optimization
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class CostBasisMethod(str, Enum):
    FIFO = "fifo"                    # First In First Out
    LIFO = "lifo"                    # Last In First Out
    AVERAGE_COST = "average_cost"    # Average Cost
    SPECIFIC_ID = "specific_id"      # Specific Identification
    HIFO = "hifo"                    # Highest In First Out (tax optimization)

class Lot:
    """
    Individual purchase lot for cost basis tracking
    """
    
    def __init__(
        self,
        lot_id: str,
        ticker: str,
        quantity: float,
        purchase_price: float,
        purchase_date: datetime,
        transaction_id: str
    ):
        self.lot_id = lot_id
        self.ticker = ticker
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.transaction_id = transaction_id
        self.remaining_quantity = quantity
        self.cost_basis = quantity * purchase_price
    
    def sell_quantity(self, quantity: float) -> Dict[str, Any]:
        """Sell quantity from this lot"""
        
        if quantity > self.remaining_quantity:
            raise ValueError("Cannot sell more than remaining quantity")
        
        proceeds_from_lot = quantity * self.purchase_price
        self.remaining_quantity -= quantity
        
        return {
            "lot_id": self.lot_id,
            "quantity_sold": quantity,
            "cost_basis": proceeds_from_lot,
            "purchase_price": self.purchase_price,
            "purchase_date": self.purchase_date
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "lot_id": self.lot_id,
            "ticker": self.ticker,
            "quantity": self.quantity,
            "remaining_quantity": self.remaining_quantity,
            "purchase_price": self.purchase_price,
            "purchase_date": self.purchase_date.isoformat(),
            "cost_basis": self.cost_basis,
            "transaction_id": self.transaction_id
        }

class PositionTracker:
    """
    Advanced position tracking with lot-level detail
    Supports multiple cost basis methods
    """
    
    def __init__(self):
        self.lots = {}  # {ticker: [Lot]}
        self.lot_counter = 0
        self.sale_history = []
    
    def add_purchase(
        self,
        ticker: str,
        quantity: float,
        purchase_price: float,
        purchase_date: datetime,
        transaction_id: str
    ) -> Lot:
        """Add purchase lot"""
        
        self.lot_counter += 1
        lot_id = f"LOT-{self.lot_counter:08d}"
        
        lot = Lot(
            lot_id=lot_id,
            ticker=ticker,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=purchase_date,
            transaction_id=transaction_id
        )
        
        if ticker not in self.lots:
            self.lots[ticker] = []
        
        self.lots[ticker].append(lot)
        
        print(f"📥 Added lot: {lot_id} ({ticker} x {quantity} @ ${purchase_price})")
        
        return lot
    
    def sell_position(
        self,
        ticker: str,
        quantity: float,
        sale_price: float,
        sale_date: datetime,
        method: CostBasisMethod = CostBasisMethod.FIFO
    ) -> Dict[str, Any]:
        """
        Sell position using specified cost basis method
        Returns realized gains/losses
        """
        
        if ticker not in self.lots:
            raise ValueError(f"No lots found for {ticker}")
        
        lots = self.lots[ticker]
        available_quantity = sum(lot.remaining_quantity for lot in lots)
        
        if quantity > available_quantity:
            raise ValueError(f"Insufficient quantity. Available: {available_quantity}")
        
        # Select lots based on method
        selected_lots = self._select_lots_for_sale(ticker, quantity, method)
        
        # Process sale
        sale_details = {
            "ticker": ticker,
            "quantity_sold": quantity,
            "sale_price": sale_price,
            "sale_date": sale_date.isoformat(),
            "sale_proceeds": quantity * sale_price,
            "lots_used": [],
            "total_cost_basis": 0,
            "realized_gl": 0,
            "method": method
        }
        
        remaining_to_sell = quantity
        
        for lot in selected_lots:
            if remaining_to_sell <= 0:
                break
            
            quantity_from_lot = min(remaining_to_sell, lot.remaining_quantity)
            
            lot_sale = lot.sell_quantity(quantity_from_lot)
            
            sale_details["lots_used"].append(lot_sale)
            sale_details["total_cost_basis"] += lot_sale["cost_basis"]
            
            remaining_to_sell -= quantity_from_lot
        
        # Calculate realized gain/loss
        sale_details["realized_gl"] = (
            sale_details["sale_proceeds"] - sale_details["total_cost_basis"]
        )
        
        sale_details["realized_gl_pct"] = (
            sale_details["realized_gl"] / sale_details["total_cost_basis"]
            if sale_details["total_cost_basis"] > 0 else 0
        )
        
        # Calculate holding period
        sale_details["holding_periods"] = self._calculate_holding_periods(
            sale_details["lots_used"],
            sale_date
        )
        
        # Store sale history
        self.sale_history.append(sale_details)
        
        print(f"💰 Sold {quantity} {ticker} @ ${sale_price}")
        print(f"   Realized G/L: ${sale_details['realized_gl']:,.2f} ({sale_details['realized_gl_pct']:.2%})")
        
        return sale_details
    
    def get_position_summary(self, ticker: str) -> Dict[str, Any]:
        """Get summary of position with all lots"""
        
        if ticker not in self.lots:
            return {
                "ticker": ticker,
                "total_quantity": 0,
                "total_cost_basis": 0,
                "average_cost": 0,
                "lots": []
            }
        
        lots = self.lots[ticker]
        active_lots = [lot for lot in lots if lot.remaining_quantity > 0]
        
        total_quantity = sum(lot.remaining_quantity for lot in active_lots)
        total_cost_basis = sum(
            lot.remaining_quantity * lot.purchase_price
            for lot in active_lots
        )
        
        return {
            "ticker": ticker,
            "total_quantity": total_quantity,
            "total_cost_basis": total_cost_basis,
            "average_cost": total_cost_basis / total_quantity if total_quantity > 0 else 0,
            "lots_count": len(active_lots),
            "lots": [lot.to_dict() for lot in active_lots]
        }
    
    def calculate_unrealized_gl(
        self,
        ticker: str,
        current_price: float
    ) -> Dict[str, Any]:
        """Calculate unrealized gains/losses"""
        
        position = self.get_position_summary(ticker)
        
        if position["total_quantity"] == 0:
            return {
                "ticker": ticker,
                "unrealized_gl": 0,
                "unrealized_gl_pct": 0
            }
        
        market_value = position["total_quantity"] * current_price
        unrealized_gl = market_value - position["total_cost_basis"]
        unrealized_gl_pct = (
            unrealized_gl / position["total_cost_basis"]
            if position["total_cost_basis"] > 0 else 0
        )
        
        return {
            "ticker": ticker,
            "quantity": position["total_quantity"],
            "cost_basis": position["total_cost_basis"],
            "average_cost": position["average_cost"],
            "current_price": current_price,
            "market_value": market_value,
            "unrealized_gl": unrealized_gl,
            "unrealized_gl_pct": unrealized_gl_pct
        }
    
    def tax_loss_harvest_opportunities(
        self,
        ticker: str,
        current_price: float,
        min_loss: float = 1000
    ) -> List[Dict[str, Any]]:
        """
        Identify tax loss harvesting opportunities
        Shows which lots could be sold for tax benefits
        """
        
        if ticker not in self.lots:
            return []
        
        opportunities = []
        
        for lot in self.lots[ticker]:
            if lot.remaining_quantity == 0:
                continue
            
            cost_basis = lot.remaining_quantity * lot.purchase_price
            market_value = lot.remaining_quantity * current_price
            potential_loss = market_value - cost_basis
            
            # Check if this is a loss position worth harvesting
            if potential_loss < -min_loss:
                opportunities.append({
                    "lot_id": lot.lot_id,
                    "quantity": lot.remaining_quantity,
                    "purchase_price": lot.purchase_price,
                    "purchase_date": lot.purchase_date.isoformat(),
                    "cost_basis": cost_basis,
                    "current_price": current_price,
                    "market_value": market_value,
                    "potential_loss": potential_loss,
                    "tax_benefit": abs(potential_loss) * 0.30  # Assume 30% tax rate
                })
        
        return sorted(opportunities, key=lambda x: x["potential_loss"])
    
    def _select_lots_for_sale(
        self,
        ticker: str,
        quantity: float,
        method: CostBasisMethod
    ) -> List[Lot]:
        """Select lots for sale based on cost basis method"""
        
        lots = [lot for lot in self.lots[ticker] if lot.remaining_quantity > 0]
        
        if method == CostBasisMethod.FIFO:
            # First In First Out
            return sorted(lots, key=lambda x: x.purchase_date)
        
        elif method == CostBasisMethod.LIFO:
            # Last In First Out
            return sorted(lots, key=lambda x: x.purchase_date, reverse=True)
        
        elif method == CostBasisMethod.HIFO:
            # Highest In First Out (minimize capital gains)
            return sorted(lots, key=lambda x: x.purchase_price, reverse=True)
        
        elif method == CostBasisMethod.AVERAGE_COST:
            # Use average cost - sell proportionally
            return lots
        
        elif method == CostBasisMethod.SPECIFIC_ID:
            # Would require user to specify which lots
            # For now, default to FIFO
            return sorted(lots, key=lambda x: x.purchase_date)
        
        return lots
    
    def _calculate_holding_periods(
        self,
        lots_used: List[Dict[str, Any]],
        sale_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate holding periods for tax classification
        <1 year = short-term, >1 year = long-term
        """
        
        short_term_quantity = 0
        long_term_quantity = 0
        
        for lot in lots_used:
            purchase_date = datetime.fromisoformat(lot["purchase_date"])
            holding_days = (sale_date - purchase_date).days
            
            if holding_days <= 365:
                short_term_quantity += lot["quantity_sold"]
            else:
                long_term_quantity += lot["quantity_sold"]
        
        return {
            "short_term_quantity": short_term_quantity,
            "long_term_quantity": long_term_quantity,
            "short_term_pct": short_term_quantity / (short_term_quantity + long_term_quantity) if (short_term_quantity + long_term_quantity) > 0 else 0,
            "long_term_pct": long_term_quantity / (short_term_quantity + long_term_quantity) if (short_term_quantity + long_term_quantity) > 0 else 0
        }

# Global instance
position_tracker = PositionTracker()
