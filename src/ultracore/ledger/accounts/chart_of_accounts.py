"""
Chart of Accounts - Australian Banking
Complete account structure for financial institution
"""
from enum import Enum
from typing import Dict, List


class AccountType(str, Enum):
    # Assets (1000-1999)
    CASH = 'CASH'
    CUSTOMER_LOANS = 'CUSTOMER_LOANS'
    FIXED_ASSETS = 'FIXED_ASSETS'
    INTANGIBLE_ASSETS = 'INTANGIBLE_ASSETS'
    
    # Liabilities (2000-2999)
    CUSTOMER_DEPOSITS = 'CUSTOMER_DEPOSITS'
    INTERBANK_BORROWINGS = 'INTERBANK_BORROWINGS'
    BONDS_PAYABLE = 'BONDS_PAYABLE'
    
    # Equity (3000-3999)
    SHARE_CAPITAL = 'SHARE_CAPITAL'
    RETAINED_EARNINGS = 'RETAINED_EARNINGS'
    RESERVES = 'RESERVES'
    
    # Income (4000-4999)
    INTEREST_INCOME = 'INTEREST_INCOME'
    FEE_INCOME = 'FEE_INCOME'
    TRADING_INCOME = 'TRADING_INCOME'
    
    # Expenses (5000-5999)
    INTEREST_EXPENSE = 'INTEREST_EXPENSE'
    OPERATING_EXPENSES = 'OPERATING_EXPENSES'
    LOAN_LOSS_PROVISION = 'LOAN_LOSS_PROVISION'


class ChartOfAccounts:
    """
    Australian Banking Chart of Accounts
    Compliant with AASB (Australian Accounting Standards Board)
    """
    
    ACCOUNTS = {
        # ASSETS
        '1000': {'name': 'Cash at Bank', 'type': AccountType.CASH, 'normal_balance': 'DEBIT'},
        '1010': {'name': 'Cash Reserve - RBA', 'type': AccountType.CASH, 'normal_balance': 'DEBIT'},
        '1100': {'name': 'Customer Loans - Personal', 'type': AccountType.CUSTOMER_LOANS, 'normal_balance': 'DEBIT'},
        '1110': {'name': 'Customer Loans - Business', 'type': AccountType.CUSTOMER_LOANS, 'normal_balance': 'DEBIT'},
        '1120': {'name': 'Customer Loans - Mortgage', 'type': AccountType.CUSTOMER_LOANS, 'normal_balance': 'DEBIT'},
        '1130': {'name': 'Allowance for Loan Losses', 'type': AccountType.CUSTOMER_LOANS, 'normal_balance': 'CREDIT'},
        '1500': {'name': 'Fixed Assets', 'type': AccountType.FIXED_ASSETS, 'normal_balance': 'DEBIT'},
        '1510': {'name': 'Accumulated Depreciation', 'type': AccountType.FIXED_ASSETS, 'normal_balance': 'CREDIT'},
        '1600': {'name': 'Intangible Assets', 'type': AccountType.INTANGIBLE_ASSETS, 'normal_balance': 'DEBIT'},
        
        # LIABILITIES
        '2000': {'name': 'Customer Deposits - Savings', 'type': AccountType.CUSTOMER_DEPOSITS, 'normal_balance': 'CREDIT'},
        '2010': {'name': 'Customer Deposits - Checking', 'type': AccountType.CUSTOMER_DEPOSITS, 'normal_balance': 'CREDIT'},
        '2020': {'name': 'Customer Deposits - Term', 'type': AccountType.CUSTOMER_DEPOSITS, 'normal_balance': 'CREDIT'},
        '2100': {'name': 'Interbank Borrowings', 'type': AccountType.INTERBANK_BORROWINGS, 'normal_balance': 'CREDIT'},
        '2200': {'name': 'Bonds Payable', 'type': AccountType.BONDS_PAYABLE, 'normal_balance': 'CREDIT'},
        
        # EQUITY
        '3000': {'name': 'Share Capital', 'type': AccountType.SHARE_CAPITAL, 'normal_balance': 'CREDIT'},
        '3100': {'name': 'Retained Earnings', 'type': AccountType.RETAINED_EARNINGS, 'normal_balance': 'CREDIT'},
        '3200': {'name': 'General Reserve', 'type': AccountType.RESERVES, 'normal_balance': 'CREDIT'},
        
        # INCOME
        '4000': {'name': 'Interest Income - Loans', 'type': AccountType.INTEREST_INCOME, 'normal_balance': 'CREDIT'},
        '4100': {'name': 'Fee Income - Account Fees', 'type': AccountType.FEE_INCOME, 'normal_balance': 'CREDIT'},
        '4110': {'name': 'Fee Income - Transaction Fees', 'type': AccountType.FEE_INCOME, 'normal_balance': 'CREDIT'},
        '4200': {'name': 'Trading Income', 'type': AccountType.TRADING_INCOME, 'normal_balance': 'CREDIT'},
        
        # EXPENSES
        '5000': {'name': 'Interest Expense - Deposits', 'type': AccountType.INTEREST_EXPENSE, 'normal_balance': 'DEBIT'},
        '5100': {'name': 'Salaries and Wages', 'type': AccountType.OPERATING_EXPENSES, 'normal_balance': 'DEBIT'},
        '5110': {'name': 'Technology Expenses', 'type': AccountType.OPERATING_EXPENSES, 'normal_balance': 'DEBIT'},
        '5120': {'name': 'Marketing Expenses', 'type': AccountType.OPERATING_EXPENSES, 'normal_balance': 'DEBIT'},
        '5200': {'name': 'Loan Loss Provision', 'type': AccountType.LOAN_LOSS_PROVISION, 'normal_balance': 'DEBIT'},
    }
    
    @classmethod
    def get_account(cls, account_code: str) -> Dict:
        return cls.ACCOUNTS.get(account_code)
    
    @classmethod
    def get_accounts_by_type(cls, account_type: AccountType) -> List[Dict]:
        return [
            {'code': code, **details}
            for code, details in cls.ACCOUNTS.items()
            if details['type'] == account_type
        ]
