# Security API Reference

This document provides a detailed API reference for the security modules.

## 1. AuthenticationService

Handles user authentication, password management, JWT tokens, and MFA.

**Initialization:**
```python
from ultracore.security.authentication import AuthenticationService

auth_service = AuthenticationService(tenant_id="YOUR-TENANT-ID", event_store=kafka_event_store)
```

**Methods:**
- `authenticate_user(...)`: Authenticate a user with password or other methods.
- `change_password(...)`: Change a user's password.
- `create_access_token(...)`: Create a JWT access token.
- `create_refresh_token(...)`: Create a JWT refresh token.
- `enable_mfa(...)`: Enable multi-factor authentication for a user.
- `hash_password(...)`: Hash a password with bcrypt.
- `reset_password(...)`: Reset a user's password.
- `validate_password_strength(...)`: Validate password strength.
- `verify_mfa(...)`: Verify an MFA code.
- `verify_password(...)`: Verify a password against a stored hash.
- `verify_token(...)`: Verify a JWT token.

## 2. AuthorizationService

Manages roles, permissions, and access control (RBAC).

**Initialization:**
```python
from ultracore.security.authorization import AuthorizationService, Permission

authz_service = AuthorizationService(tenant_id="YOUR-TENANT-ID", event_store=kafka_event_store)
```

**Methods:**
- `assign_role(...)`: Assign a role to a user.
- `check_permission(...)`: Check if a user has a specific permission.
- `create_permission(...)`: Create a new permission.
- `create_role(...)`: Create a new role.
- `delete_permission(...)`: Delete a permission.
- `delete_role(...)`: Delete a role.
- `get_role_permissions(...)`: Get all permissions for a role.
- `get_user_roles(...)`: Get all roles for a user.
- `grant_permission(...)`: Grant a permission to a role.
- `has_permission(...)`: Check if a user has a permission (alias for `check_permission`).
- `revoke_permission(...)`: Revoke a permission from a role.
- `revoke_role(...)`: Revoke a role from a user.

## 3. EncryptionService

Provides symmetric encryption (Fernet), hashing, and key derivation.

**Initialization:**
```python
from ultracore.security.encryption import EncryptionService

encryption_service = EncryptionService(tenant_id="YOUR-TENANT-ID", event_store=kafka_event_store)
```

**Methods:**
- `decrypt(...)`: Decrypt data with Fernet.
- `decrypt_field(...)`: Decrypt a specific field.
- `decrypt_sensitive_data(...)`: Decrypt sensitive fields in a dictionary.
- `derive_key_from_password(...)`: Derive an encryption key from a password.
- `encrypt(...)`: Encrypt data with Fernet.
- `encrypt_field(...)`: Encrypt a specific field.
- `encrypt_sensitive_data(...)`: Encrypt sensitive fields in a dictionary.
- `generate_key()`: Generate a new Fernet key.
- `get_key()`: Get the current encryption key.
- `hash_data(...)`: Hash data with SHA256, SHA512, or SHA1.
