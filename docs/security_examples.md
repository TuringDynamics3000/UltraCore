# Security Usage Examples

This document provides practical examples of how to use the security modules.

## 1. Authenticating a User

```python
from ultracore.security.authentication import AuthenticationService

async def authenticate_user_example(user_id, password, stored_hash):
    auth_service = AuthenticationService(tenant_id="YOUR-TENANT-ID", event_store=kafka_event_store)
    
    is_authenticated = await auth_service.authenticate_user(
        user_id=user_id,
        password=password,
        stored_hash=stored_hash,
        authentication_method="password",
        ip_address="127.0.0.1",
        user_agent="ExampleApp/1.0"
    )
    
    if is_authenticated:
        print(f"User {user_id} authenticated successfully!")
        # Create a JWT token
        token = auth_service.create_access_token({"user_id": user_id})
        print(f"JWT Token: {token}")
    else:
        print(f"Authentication failed for user {user_id}")
```

## 2. Managing Roles and Permissions

```python
from ultracore.security.authorization import AuthorizationService, Permission

async def manage_permissions_example(user_id):
    authz_service = AuthorizationService(tenant_id="YOUR-TENANT-ID", event_store=kafka_event_store)
    
    # Create a new role
    await authz_service.create_role("admin", "Administrator role with full access")
    
    # Grant permissions to the role
    await authz_service.grant_permission("admin", Permission.CREATE, "system")
    await authz_service.grant_permission("admin", Permission.READ, "system")
    await authz_service.grant_permission("admin", Permission.UPDATE, "system")
    await authz_service.grant_permission("admin", Permission.DELETE, "system")
    
    # Assign the role to a user
    await authz_service.assign_role(user_id, "admin", "system")
    
    # Check if the user has permission
    if authz_service.has_permission(user_id, Permission.DELETE):
        print(f"User {user_id} has DELETE permission!")
    else:
        print(f"User {user_id} does NOT have DELETE permission.")
```

## 3. Encrypting and Decrypting Data

```python
from ultracore.security.encryption import EncryptionService

async def encrypt_data_example(data_to_encrypt):
    encryption_service = EncryptionService(tenant_id="YOUR-TENANT-ID", event_store=kafka_event_store)
    
    # Encrypt data
    encrypted_data = await encryption_service.encrypt(
        data=data_to_encrypt,
        user_id="system",
        data_type="user_profile",
        field_name="ssn"
    )
    
    print(f"Original data: {data_to_encrypt}")
    print(f"Encrypted data: {encrypted_data}")
    
    # Decrypt data
    decrypted_data = encryption_service.decrypt(encrypted_data)
    print(f"Decrypted data: {decrypted_data}")
```
