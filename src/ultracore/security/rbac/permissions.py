"""
RBAC - Role-Based Access Control
Permission system for UltraCore Digital Bank

Digital-only bank: No tellers, no branches, API-first
"""
from typing import List, Optional, Set
from enum import Enum
from fastapi import HTTPException, Depends

from ultracore.security.auth.jwt_auth import User, get_current_user


class Permission(str, Enum):
    # Account permissions
    ACCOUNT_CREATE = 'account:create'
    ACCOUNT_READ = 'account:read'
    ACCOUNT_UPDATE = 'account:update'
    ACCOUNT_DELETE = 'account:delete'
    ACCOUNT_CLOSE = 'account:close'
    
    # Payment permissions
    PAYMENT_INITIATE = 'payment:initiate'
    PAYMENT_APPROVE = 'payment:approve'
    PAYMENT_READ = 'payment:read'
    PAYMENT_CANCEL = 'payment:cancel'
    PAYMENT_BULK = 'payment:bulk'
    
    # Loan permissions
    LOAN_CREATE = 'loan:create'
    LOAN_APPROVE = 'loan:approve'
    LOAN_READ = 'loan:read'
    LOAN_MODIFY = 'loan:modify'
    
    # Card permissions
    CARD_ISSUE = 'card:issue'
    CARD_BLOCK = 'card:block'
    CARD_UNBLOCK = 'card:unblock'
    CARD_READ = 'card:read'
    CARD_LIMITS = 'card:limits'
    
    # GL permissions
    GL_POST = 'gl:post'
    GL_READ = 'gl:read'
    GL_RECONCILE = 'gl:reconcile'
    GL_REPORTS = 'gl:reports'
    
    # Customer support permissions
    SUPPORT_VIEW_CUSTOMER = 'support:view_customer'
    SUPPORT_ASSIST = 'support:assist'
    SUPPORT_ESCALATE = 'support:escalate'
    
    # Compliance permissions
    COMPLIANCE_VIEW_ALL = 'compliance:view_all'
    COMPLIANCE_REPORTS = 'compliance:reports'
    COMPLIANCE_INVESTIGATIONS = 'compliance:investigations'
    
    # Data & Analytics permissions
    ANALYTICS_READ = 'analytics:read'
    ANALYTICS_CREATE = 'analytics:create'
    DATA_EXPORT = 'data:export'
    
    # Risk permissions
    RISK_ASSESSMENT = 'risk:assessment'
    RISK_LIMITS = 'risk:limits'
    
    # User management
    USER_CREATE = 'user:create'
    USER_READ = 'user:read'
    USER_UPDATE = 'user:update'
    USER_DELETE = 'user:delete'
    
    # API permissions
    API_FULL_ACCESS = 'api:full_access'
    API_READ_ONLY = 'api:read_only'
    
    # Admin permissions
    ADMIN_FULL = 'admin:full'


class Role(str, Enum):
    """
    Digital-Only Bank Roles
    
    No physical branches - all digital
    """
    # Executive/Admin
    SUPER_ADMIN = 'SUPER_ADMIN'
    ADMIN = 'ADMIN'
    
    # Operations
    OPERATIONS_MANAGER = 'OPERATIONS_MANAGER'
    OPERATIONS_ANALYST = 'OPERATIONS_ANALYST'
    
    # Finance & Accounting
    ACCOUNTANT = 'ACCOUNTANT'
    FINANCIAL_CONTROLLER = 'FINANCIAL_CONTROLLER'
    
    # Customer Support (Digital-first)
    CUSTOMER_SUPPORT_L1 = 'CUSTOMER_SUPPORT_L1'  # Level 1 support
    CUSTOMER_SUPPORT_L2 = 'CUSTOMER_SUPPORT_L2'  # Level 2 support
    CUSTOMER_SUPPORT_MANAGER = 'CUSTOMER_SUPPORT_MANAGER'
    
    # Compliance & Risk
    COMPLIANCE_OFFICER = 'COMPLIANCE_OFFICER'
    RISK_ANALYST = 'RISK_ANALYST'
    FRAUD_ANALYST = 'FRAUD_ANALYST'
    
    # Lending
    LOAN_OFFICER = 'LOAN_OFFICER'
    CREDIT_ANALYST = 'CREDIT_ANALYST'
    
    # Data & Analytics
    DATA_ANALYST = 'DATA_ANALYST'
    DATA_SCIENTIST = 'DATA_SCIENTIST'
    
    # Engineering/Development
    DEVELOPER = 'DEVELOPER'
    DEVOPS = 'DEVOPS'
    
    # End Users
    CUSTOMER = 'CUSTOMER'  # End customer using the app
    
    # External Integrations
    API_CLIENT = 'API_CLIENT'
    PARTNER_API = 'PARTNER_API'


class RolePermissions:
    """Role to permissions mapping for digital-only bank"""
    
    ROLE_PERMISSIONS = {
        # Executive/Admin Roles
        Role.SUPER_ADMIN: [Permission.ADMIN_FULL],  # All permissions
        
        Role.ADMIN: [
            Permission.ACCOUNT_CREATE,
            Permission.ACCOUNT_READ,
            Permission.ACCOUNT_UPDATE,
            Permission.ACCOUNT_DELETE,
            Permission.PAYMENT_APPROVE,
            Permission.PAYMENT_READ,
            Permission.LOAN_APPROVE,
            Permission.LOAN_READ,
            Permission.CARD_ISSUE,
            Permission.CARD_BLOCK,
            Permission.CARD_READ,
            Permission.GL_READ,
            Permission.GL_REPORTS,
            Permission.USER_CREATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.COMPLIANCE_VIEW_ALL,
            Permission.ANALYTICS_READ,
        ],
        
        # Operations Roles
        Role.OPERATIONS_MANAGER: [
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_APPROVE,
            Permission.PAYMENT_READ,
            Permission.PAYMENT_BULK,
            Permission.LOAN_APPROVE,
            Permission.LOAN_READ,
            Permission.GL_READ,
            Permission.GL_REPORTS,
            Permission.GL_RECONCILE,
            Permission.ANALYTICS_READ,
            Permission.RISK_ASSESSMENT,
        ],
        
        Role.OPERATIONS_ANALYST: [
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.LOAN_READ,
            Permission.GL_READ,
            Permission.ANALYTICS_READ,
        ],
        
        # Finance & Accounting Roles
        Role.ACCOUNTANT: [
            Permission.GL_POST,
            Permission.GL_READ,
            Permission.GL_RECONCILE,
            Permission.GL_REPORTS,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.ANALYTICS_READ,
        ],
        
        Role.FINANCIAL_CONTROLLER: [
            Permission.GL_POST,
            Permission.GL_READ,
            Permission.GL_RECONCILE,
            Permission.GL_REPORTS,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.LOAN_READ,
            Permission.ANALYTICS_READ,
            Permission.ANALYTICS_CREATE,
            Permission.DATA_EXPORT,
        ],
        
        # Customer Support Roles (Digital-first)
        Role.CUSTOMER_SUPPORT_L1: [
            Permission.ACCOUNT_READ,
            Permission.SUPPORT_VIEW_CUSTOMER,
            Permission.SUPPORT_ASSIST,
            Permission.PAYMENT_READ,
            Permission.CARD_READ,
        ],
        
        Role.CUSTOMER_SUPPORT_L2: [
            Permission.ACCOUNT_READ,
            Permission.ACCOUNT_UPDATE,
            Permission.SUPPORT_VIEW_CUSTOMER,
            Permission.SUPPORT_ASSIST,
            Permission.SUPPORT_ESCALATE,
            Permission.PAYMENT_READ,
            Permission.PAYMENT_CANCEL,
            Permission.CARD_READ,
            Permission.CARD_BLOCK,
            Permission.CARD_UNBLOCK,
        ],
        
        Role.CUSTOMER_SUPPORT_MANAGER: [
            Permission.ACCOUNT_READ,
            Permission.ACCOUNT_UPDATE,
            Permission.ACCOUNT_CLOSE,
            Permission.SUPPORT_VIEW_CUSTOMER,
            Permission.SUPPORT_ASSIST,
            Permission.SUPPORT_ESCALATE,
            Permission.PAYMENT_READ,
            Permission.PAYMENT_APPROVE,
            Permission.PAYMENT_CANCEL,
            Permission.CARD_READ,
            Permission.CARD_BLOCK,
            Permission.CARD_UNBLOCK,
            Permission.CARD_ISSUE,
            Permission.ANALYTICS_READ,
        ],
        
        # Compliance & Risk Roles
        Role.COMPLIANCE_OFFICER: [
            Permission.COMPLIANCE_VIEW_ALL,
            Permission.COMPLIANCE_REPORTS,
            Permission.COMPLIANCE_INVESTIGATIONS,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.LOAN_READ,
            Permission.GL_READ,
            Permission.GL_REPORTS,
            Permission.ANALYTICS_READ,
            Permission.DATA_EXPORT,
        ],
        
        Role.RISK_ANALYST: [
            Permission.RISK_ASSESSMENT,
            Permission.RISK_LIMITS,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.LOAN_READ,
            Permission.ANALYTICS_READ,
            Permission.ANALYTICS_CREATE,
        ],
        
        Role.FRAUD_ANALYST: [
            Permission.RISK_ASSESSMENT,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.CARD_BLOCK,
            Permission.ANALYTICS_READ,
            Permission.COMPLIANCE_INVESTIGATIONS,
        ],
        
        # Lending Roles
        Role.LOAN_OFFICER: [
            Permission.LOAN_CREATE,
            Permission.LOAN_READ,
            Permission.LOAN_MODIFY,
            Permission.ACCOUNT_READ,
            Permission.RISK_ASSESSMENT,
        ],
        
        Role.CREDIT_ANALYST: [
            Permission.LOAN_READ,
            Permission.LOAN_APPROVE,
            Permission.ACCOUNT_READ,
            Permission.RISK_ASSESSMENT,
            Permission.ANALYTICS_READ,
        ],
        
        # Data & Analytics Roles
        Role.DATA_ANALYST: [
            Permission.ANALYTICS_READ,
            Permission.ANALYTICS_CREATE,
            Permission.DATA_EXPORT,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.LOAN_READ,
        ],
        
        Role.DATA_SCIENTIST: [
            Permission.ANALYTICS_READ,
            Permission.ANALYTICS_CREATE,
            Permission.DATA_EXPORT,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.LOAN_READ,
            Permission.GL_READ,
        ],
        
        # Engineering/Development Roles
        Role.DEVELOPER: [
            Permission.API_FULL_ACCESS,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
            Permission.ANALYTICS_READ,
        ],
        
        Role.DEVOPS: [
            Permission.API_FULL_ACCESS,
            Permission.ANALYTICS_READ,
        ],
        
        # End User Role (Mobile App Users)
        Role.CUSTOMER: [
            Permission.ACCOUNT_READ,  # View own account
            Permission.PAYMENT_INITIATE,  # Make payments
            Permission.PAYMENT_READ,  # View own payments
            Permission.CARD_READ,  # View own cards
            Permission.CARD_LIMITS,  # Set card limits
            Permission.LOAN_READ,  # View own loans
        ],
        
        # External Integration Roles
        Role.API_CLIENT: [
            Permission.API_READ_ONLY,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_READ,
        ],
        
        Role.PARTNER_API: [
            Permission.API_FULL_ACCESS,
            Permission.ACCOUNT_CREATE,
            Permission.ACCOUNT_READ,
            Permission.PAYMENT_INITIATE,
            Permission.PAYMENT_READ,
        ]
    }
    
    @classmethod
    def get_permissions(cls, role: Role) -> Set[Permission]:
        """Get all permissions for a role"""
        if role == Role.SUPER_ADMIN:
            # Super admin has all permissions
            return set(Permission)
        
        return set(cls.ROLE_PERMISSIONS.get(role, []))
    
    @classmethod
    def get_user_permissions(cls, user: User) -> Set[Permission]:
        """Get all permissions for a user based on their roles"""
        permissions = set()
        
        for role_str in user.roles:
            try:
                role = Role(role_str)
                permissions.update(cls.get_permissions(role))
            except ValueError:
                continue
        
        return permissions


class PermissionChecker:
    """Check if user has required permissions"""
    
    @staticmethod
    def has_permission(user: User, required_permission: Permission) -> bool:
        """Check if user has a specific permission"""
        user_permissions = RolePermissions.get_user_permissions(user)
        
        # Super admin has all permissions
        if Permission.ADMIN_FULL in user_permissions:
            return True
        
        return required_permission in user_permissions
    
    @staticmethod
    def require_permission(required_permission: Permission):
        """
        Decorator to require specific permission
        
        Usage:
        @require_permission(Permission.PAYMENT_APPROVE)
        async def approve_payment(...):
            ...
        """
        async def permission_checker(user: User = Depends(get_current_user)):
            if not PermissionChecker.has_permission(user, required_permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {required_permission.value} required"
                )
            return user
        
        return permission_checker
    
    @staticmethod
    def require_any_permission(required_permissions: List[Permission]):
        """Require at least one of the specified permissions"""
        async def permission_checker(user: User = Depends(get_current_user)):
            user_permissions = RolePermissions.get_user_permissions(user)
            
            # Check if user has any of the required permissions
            if Permission.ADMIN_FULL in user_permissions:
                return user
            
            if not any(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: One of {[p.value for p in required_permissions]} required"
                )
            return user
        
        return permission_checker
    
    @staticmethod
    def require_all_permissions(required_permissions: List[Permission]):
        """Require all specified permissions"""
        async def permission_checker(user: User = Depends(get_current_user)):
            user_permissions = RolePermissions.get_user_permissions(user)
            
            # Super admin has all permissions
            if Permission.ADMIN_FULL in user_permissions:
                return user
            
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: All of {[p.value for p in required_permissions]} required"
                )
            return user
        
        return permission_checker


# Convenience functions for common role checks
def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin or super admin role"""
    if not any(role in [Role.ADMIN.value, Role.SUPER_ADMIN.value] for role in user.roles):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


def require_super_admin(user: User = Depends(get_current_user)) -> User:
    """Require super admin role"""
    if Role.SUPER_ADMIN.value not in user.roles:
        raise HTTPException(status_code=403, detail="Super admin privileges required")
    return user


def require_customer_support(user: User = Depends(get_current_user)) -> User:
    """Require customer support role (any level)"""
    support_roles = [
        Role.CUSTOMER_SUPPORT_L1.value,
        Role.CUSTOMER_SUPPORT_L2.value,
        Role.CUSTOMER_SUPPORT_MANAGER.value
    ]
    if not any(role in support_roles for role in user.roles):
        raise HTTPException(status_code=403, detail="Customer support privileges required")
    return user


def require_compliance(user: User = Depends(get_current_user)) -> User:
    """Require compliance officer role"""
    if Role.COMPLIANCE_OFFICER.value not in user.roles:
        raise HTTPException(status_code=403, detail="Compliance officer privileges required")
    return user
