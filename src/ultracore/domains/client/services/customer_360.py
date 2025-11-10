"""
Customer 360 View Service
Aggregates all customer data across domains
"""
from typing import Dict, List, Optional
from ultracore.infrastructure.event_store.store import get_event_store


class Customer360Service:
    """
    Provides comprehensive customer view
    Aggregates data from all domains
    """
    
    async def get_customer_360(self, customer_id: str) -> Dict:
        """
        Get complete customer view
        """
        store = get_event_store()
        
        # Get all events for customer
        customer_events = await store.get_events(customer_id)
        
        # Get related loan events
        all_events = await store.get_all_events(limit=10000)
        loan_events = [
            e for e in all_events 
            if e.aggregate_type == 'Loan' and 
            e.event_data.get('customer_id') == customer_id
        ]
        
        # Build customer profile
        profile = self._build_profile(customer_events)
        
        # Build financial summary
        financial_summary = self._build_financial_summary(loan_events)
        
        # Build activity timeline
        activity = self._build_activity_timeline(customer_events + loan_events)
        
        # Calculate customer value
        customer_value = self._calculate_customer_value(loan_events)
        
        return {
            'customer_id': customer_id,
            'profile': profile,
            'financial_summary': financial_summary,
            'activity_timeline': activity[-20:],  # Last 20 activities
            'customer_value': customer_value,
            'relationships': {
                'total_loans': len([e for e in loan_events if e.event_type == 'LoanApplied']),
                'active_loans': len([e for e in loan_events if e.event_type == 'LoanApproved']),
            }
        }
    
    def _build_profile(self, events: List) -> Dict:
        """Build customer profile from events"""
        profile = {
            'kyc_status': 'NOT_STARTED',
            'risk_score': None,
            'status': 'PENDING'
        }
        
        for event in events:
            if event.event_type == 'CustomerOnboarded':
                profile.update({
                    'first_name': event.event_data.get('first_name'),
                    'last_name': event.event_data.get('last_name'),
                    'email': event.event_data.get('email'),
                    'phone': event.event_data.get('phone'),
                    'onboarded_at': event.event_data.get('onboarded_at'),
                    'status': 'ACTIVE'
                })
            elif event.event_type == 'KYCVerified':
                profile.update({
                    'kyc_status': 'VERIFIED',
                    'risk_score': event.event_data.get('risk_score')
                })
        
        return profile
    
    def _build_financial_summary(self, loan_events: List) -> Dict:
        """Build financial summary"""
        total_borrowed = 0
        total_approved = 0
        total_rejected = 0
        
        for event in loan_events:
            if event.event_type == 'LoanApplied':
                amount = float(event.event_data.get('amount', 0))
                total_borrowed += amount
            elif event.event_type == 'LoanApproved':
                total_approved += 1
            elif event.event_type == 'LoanRejected':
                total_rejected += 1
        
        return {
            'total_borrowed': total_borrowed,
            'total_loans_approved': total_approved,
            'total_loans_rejected': total_rejected,
            'approval_rate': total_approved / (total_approved + total_rejected) if (total_approved + total_rejected) > 0 else 0
        }
    
    def _build_activity_timeline(self, events: List) -> List[Dict]:
        """Build activity timeline"""
        return [
            {
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type,
                'aggregate_type': event.aggregate_type,
                'description': self._event_description(event)
            }
            for event in sorted(events, key=lambda e: e.timestamp, reverse=True)
        ]
    
    def _event_description(self, event) -> str:
        """Generate human-readable event description"""
        descriptions = {
            'CustomerOnboarded': 'Customer account created',
            'KYCInitiated': 'KYC verification started',
            'KYCVerified': 'Identity verified',
            'LoanApplied': f'Applied for loan of ',
            'LoanApproved': 'Loan approved',
            'LoanRejected': 'Loan rejected'
        }
        return descriptions.get(event.event_type, event.event_type)
    
    def _calculate_customer_value(self, loan_events: List) -> Dict:
        """Calculate customer lifetime value"""
        # Simple calculation - in production would be more sophisticated
        total_loan_value = sum(
            float(e.event_data.get('amount', 0))
            for e in loan_events
            if e.event_type == 'LoanApproved'
        )
        
        return {
            'lifetime_value': total_loan_value,
            'segment': 'HIGH_VALUE' if total_loan_value > 100000 else 'MEDIUM_VALUE' if total_loan_value > 50000 else 'STANDARD'
        }


customer_360_service = Customer360Service()
