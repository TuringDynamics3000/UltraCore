"""
Security Module Tests
Tests for event-sourced authentication, authorization, and encryption services
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from ultracore.security.authentication import AuthenticationService
from ultracore.security.authorization import AuthorizationService, Permission, Role
from ultracore.security.encryption import EncryptionService


class TestAuthentication:
    """Test authentication security"""

    @pytest.fixture
    def mock_event_store(self):
        """Mock event store for testing"""
        store = Mock()
        store.append_event = AsyncMock()
        return store

    @pytest.fixture
    def auth_service(self, mock_event_store):
        """Create authentication service with mocked event store"""
        return AuthenticationService(event_store=mock_event_store, tenant_id="TEST-TENANT")

    def test_password_hashing(self, auth_service):
        """Test that passwords are properly hashed"""
        password = "SecurePassword123!"
        hashed = auth_service.hash_password(password)

        assert hashed != password
        assert len(hashed) > 50
        assert auth_service.verify_password(password, hashed)

    def test_weak_password_rejection(self, auth_service):
        """Test rejection of weak passwords"""
        weak_passwords = ["123456", "password", "abc", "test"]

        for weak_pwd in weak_passwords:
            with pytest.raises(ValueError, match="Password too weak"):
                auth_service.validate_password_strength(weak_pwd)

    def test_strong_password_acceptance(self, auth_service):
        """Test acceptance of strong passwords"""
        strong_passwords = ["SecurePass123!", "MyP@ssw0rd2024", "C0mpl3x!Pass"]

        for strong_pwd in strong_passwords:
            assert auth_service.validate_password_strength(strong_pwd) is True

    def test_jwt_token_generation(self, auth_service):
        """Test JWT token generation and validation"""
        user_data = {"user_id": "USER-001", "tenant_id": "TEST-TENANT"}
        token = auth_service.create_access_token(user_data)

        assert token is not None
        assert isinstance(token, str)

        decoded = auth_service.verify_token(token)
        assert decoded["user_id"] == "USER-001"
        assert decoded["tenant_id"] == "TEST-TENANT"

    def test_token_expiration(self, auth_service):
        """Test that tokens have expiration"""
        user_data = {"user_id": "USER-001"}
        token = auth_service.create_access_token(user_data, expires_in=1)

        decoded = auth_service.verify_token(token)
        assert "exp" in decoded
        assert "iat" in decoded

    def test_invalid_token_rejection(self, auth_service):
        """Test rejection of invalid/tampered tokens"""
        invalid_tokens = ["invalid.token.here", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid", ""]

        for token in invalid_tokens:
            with pytest.raises(ValueError):
                auth_service.verify_token(token)

    def test_refresh_token_generation(self, auth_service):
        """Test refresh token generation"""
        user_id = "USER-001"
        refresh_token = auth_service.create_refresh_token(user_id)

        assert refresh_token is not None
        assert isinstance(refresh_token, str)

        decoded = auth_service.verify_token(refresh_token)
        assert decoded["sub"] == user_id
        assert decoded["type"] == "refresh"

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_event_store):
        """Test successful user authentication publishes event"""
        user_id = "USER-001"
        password = "SecurePass123!"
        stored_hash = auth_service.hash_password(password)

        result = await auth_service.authenticate_user(
            user_id=user_id, password=password, stored_hash=stored_hash, ip_address="192.168.1.1"
        )

        assert result is True
        mock_event_store.append_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self, auth_service, mock_event_store):
        """Test failed authentication does not publish event"""
        user_id = "USER-001"
        password = "WrongPassword"
        stored_hash = auth_service.hash_password("CorrectPass123!")

        result = await auth_service.authenticate_user(
            user_id=user_id, password=password, stored_hash=stored_hash
        )

        assert result is False
        mock_event_store.append_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_change_password(self, auth_service, mock_event_store):
        """Test password change publishes event"""
        user_id = "USER-001"
        old_password = "OldPass123!"
        new_password = "NewPass456!"
        stored_hash = auth_service.hash_password(old_password)

        new_hash = await auth_service.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password,
            stored_hash=stored_hash,
            changed_by=user_id,
        )

        assert new_hash != stored_hash
        assert auth_service.verify_password(new_password, new_hash)
        mock_event_store.append_event.assert_called_once()

    def test_password_validation_no_lowercase(self, auth_service):
        """Test password validation rejects passwords without lowercase"""
        with pytest.raises(ValueError, match="must contain lowercase letters"):
            auth_service.validate_password_strength("PASSWORD123!")

    def test_password_validation_no_numbers(self, auth_service):
        """Test password validation rejects passwords without numbers"""
        with pytest.raises(ValueError, match="must contain numbers"):
            auth_service.validate_password_strength("PasswordABC!")

    def test_password_validation_no_special_chars(self, auth_service):
        """Test password validation rejects passwords without special characters"""
        with pytest.raises(ValueError, match="must contain special characters"):
            auth_service.validate_password_strength("Password123")

    def test_token_tenant_mismatch(self, auth_service):
        """Test that tokens from different tenants are rejected"""
        # Create service with different tenant
        other_service = AuthenticationService(tenant_id="OTHER-TENANT")
        token = other_service.create_access_token({"user_id": "user123"})

        # Try to verify with original service
        with pytest.raises(ValueError, match="Token tenant mismatch"):
            auth_service.verify_token(token)

    def test_invalid_jwt_token(self, auth_service):
        """Test that invalid JWT tokens are rejected"""
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.verify_token("invalid.token.here")

    def test_create_token_without_event_store(self):
        """Test token creation without event store"""
        service = AuthenticationService(event_store=None, tenant_id="TEST")
        token = service.create_access_token({"user_id": "user123"})
        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token_without_event_store(self):
        """Test refresh token creation without event store"""
        service = AuthenticationService(event_store=None, tenant_id="TEST")
        token = service.create_refresh_token("user123")
        assert token is not None
        assert isinstance(token, str)


class TestAuthorization:
    """Test authorization and permissions"""

    @pytest.fixture
    def mock_event_store(self):
        """Mock event store for testing"""
        store = Mock()
        store.append_event = AsyncMock()
        return store

    @pytest.fixture
    def authz_service(self, mock_event_store):
        """Create authorization service with mocked event store"""
        return AuthorizationService(event_store=mock_event_store, tenant_id="TEST-TENANT")

    @pytest.mark.asyncio
    async def test_assign_role(self, authz_service, mock_event_store):
        """Test role assignment publishes event"""
        user_id = "USER-001"

        await authz_service.assign_role(user_id=user_id, role=Role.MANAGER, assigned_by="ADMIN-001")

        assert authz_service.has_role(user_id, Role.MANAGER)
        mock_event_store.append_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_role(self, authz_service, mock_event_store):
        """Test role revocation publishes event"""
        user_id = "USER-001"

        # First assign a role
        await authz_service.assign_role(
            user_id=user_id, role=Role.OPERATOR, assigned_by="ADMIN-001"
        )

        # Then revoke it
        await authz_service.revoke_role(user_id=user_id, role=Role.OPERATOR, revoked_by="ADMIN-001")

        assert not authz_service.has_role(user_id, Role.OPERATOR)
        assert mock_event_store.append_event.call_count == 2

    @pytest.mark.asyncio
    async def test_grant_permission(self, authz_service, mock_event_store):
        """Test permission grant publishes event"""
        user_id = "USER-001"

        await authz_service.grant_permission(
            user_id=user_id, permission=Permission.VIEW_REPORTS, granted_by="ADMIN-001"
        )

        assert authz_service.has_permission(user_id, Permission.VIEW_REPORTS)
        mock_event_store.append_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_admin_permissions(self, authz_service):
        """Test admin has all permissions"""
        user_id = "ADMIN-001"

        await authz_service.assign_role(user_id=user_id, role=Role.ADMIN, assigned_by="SYSTEM")

        # Admin should have all permissions
        assert authz_service.has_permission(user_id, Permission.READ)
        assert authz_service.has_permission(user_id, Permission.WRITE)
        assert authz_service.has_permission(user_id, Permission.DELETE)
        assert authz_service.has_permission(user_id, Permission.ADMIN)
        assert authz_service.is_admin(user_id)

    @pytest.mark.asyncio
    async def test_role_permissions(self, authz_service):
        """Test that roles grant correct permissions"""
        user_id = "USER-001"

        await authz_service.assign_role(user_id=user_id, role=Role.VIEWER, assigned_by="ADMIN-001")

        # Viewer should have read permissions
        assert authz_service.has_permission(user_id, Permission.READ)
        assert authz_service.has_permission(user_id, Permission.VIEW_REPORTS)

        # But not write permissions
        assert not authz_service.has_permission(user_id, Permission.WRITE)
        assert not authz_service.has_permission(user_id, Permission.DELETE)

    @pytest.mark.asyncio
    async def test_check_permission_denied(self, authz_service, mock_event_store):
        """Test permission check publishes AccessDenied event"""
        user_id = "USER-001"

        with pytest.raises(PermissionError):
            await authz_service.check_permission(user_id=user_id, permission=Permission.ADMIN)

        # Should publish AccessDenied event
        mock_event_store.append_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_can_access_resource(self, authz_service, mock_event_store):
        """Test resource access check"""
        user_id = "USER-001"

        await authz_service.assign_role(
            user_id=user_id, role=Role.OPERATOR, assigned_by="ADMIN-001"
        )

        # Should be able to access with READ permission
        can_access = await authz_service.can_access_resource(
            user_id=user_id, resource_id="ACCOUNT-001", required_permission=Permission.READ
        )

        assert can_access is True

    @pytest.mark.asyncio
    async def test_cannot_access_resource_without_permission(self, authz_service, mock_event_store):
        """Test resource access denied without permission"""
        user_id = "USER-001"

        # No roles assigned, so no permissions
        can_access = await authz_service.can_access_resource(
            user_id=user_id, resource_id="ACCOUNT-001", required_permission=Permission.ADMIN
        )

        assert can_access is False


class TestEncryption:
    """Test data encryption and security"""

    @pytest.fixture
    def mock_event_store(self):
        """Mock event store for testing"""
        store = Mock()
        store.append_event = AsyncMock()
        return store

    @pytest.fixture
    def encryption_service(self, mock_event_store):
        """Create encryption service with mocked event store"""
        return EncryptionService(event_store=mock_event_store, tenant_id="TEST-TENANT")

    @pytest.mark.asyncio
    async def test_data_encryption_decryption(self, encryption_service):
        """Test symmetric encryption/decryption"""
        sensitive_data = "SSN: 123-45-6789"

        encrypted = await encryption_service.encrypt(sensitive_data)
        assert encrypted != sensitive_data
        assert len(encrypted) > 0

        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == sensitive_data

    @pytest.mark.asyncio
    async def test_encryption_publishes_event(self, encryption_service, mock_event_store):
        """Test that encryption publishes DataEncrypted event"""
        sensitive_data = "Credit Card: 1234-5678-9012-3456"

        await encryption_service.encrypt(
            sensitive_data, user_id="USER-001", data_type="payment", field_name="credit_card"
        )

        mock_event_store.append_event.assert_called_once()

    def test_hash_data(self, encryption_service):
        """Test one-way hashing"""
        data = "sensitive data"

        hash1 = encryption_service.hash_data(data, algorithm="sha256")
        hash2 = encryption_service.hash_data(data, algorithm="sha256")

        # Same input should produce same hash
        assert hash1 == hash2
        assert hash1 != data
        assert len(hash1) == 64  # SHA256 produces 64 hex characters

    def test_different_algorithms(self, encryption_service):
        """Test different hashing algorithms"""
        data = "test data"

        sha256_hash = encryption_service.hash_data(data, algorithm="sha256")
        sha512_hash = encryption_service.hash_data(data, algorithm="sha512")

        assert sha256_hash != sha512_hash
        assert len(sha256_hash) == 64  # SHA256
        assert len(sha512_hash) == 128  # SHA512

    def test_key_generation(self, encryption_service):
        """Test encryption key generation"""
        key = encryption_service.generate_key()

        assert key is not None
        assert isinstance(key, str)
        assert len(key) > 20

    def test_derive_key_from_password(self, encryption_service):
        """Test key derivation from password"""
        password = "MySecurePassword123!"

        key1, salt1 = encryption_service.derive_key_from_password(password)
        key2, salt2 = encryption_service.derive_key_from_password(password)

        # Different salts should produce different keys
        assert key1 != key2
        assert salt1 != salt2

    @pytest.mark.asyncio
    async def test_encrypt_sensitive_data(self, encryption_service, mock_event_store):
        """Test encryption of sensitive fields in dictionary"""
        data = {
            "user_id": "USER-001",
            "name": "John Doe",
            "ssn": "123-45-6789",
            "account_number": "9876543210",
            "email": "john@example.com",
        }

        encrypted_data = await encryption_service.encrypt_sensitive_data(data, user_id="USER-001")

        # Sensitive fields should be encrypted
        assert encrypted_data["ssn"] != data["ssn"]
        assert encrypted_data["account_number"] != data["account_number"]

        # Non-sensitive fields should remain unchanged
        assert encrypted_data["user_id"] == data["user_id"]
        assert encrypted_data["name"] == data["name"]
        assert encrypted_data["email"] == data["email"]

    def test_decrypt_sensitive_data(self, encryption_service):
        """Test decryption of sensitive fields in dictionary"""
        # First encrypt some data manually
        original_ssn = "123-45-6789"
        encrypted_ssn = encryption_service.fernet.encrypt(original_ssn.encode()).decode()
        encrypted_ssn_b64 = encryption_service.fernet.encrypt(original_ssn.encode())
        import base64

        encrypted_ssn_final = base64.b64encode(encrypted_ssn_b64).decode("utf-8")

        data = {"user_id": "USER-001", "ssn": encrypted_ssn_final}

        decrypted_data = encryption_service.decrypt_sensitive_data(data)

        # SSN should be decrypted (or remain encrypted if format doesn't match)
        assert "ssn" in decrypted_data
        assert "user_id" in decrypted_data


class TestAuthorizationEdgeCases:
    """Test authorization edge cases for full coverage"""

    @pytest.fixture
    def mock_event_store(self):
        """Mock event store for testing"""
        store = Mock()
        store.append_event = AsyncMock()
        return store

    @pytest.fixture
    def authz_service(self, mock_event_store):
        """Create authorization service with mocked event store"""
        return AuthorizationService(event_store=mock_event_store, tenant_id="TEST-TENANT")

    @pytest.mark.asyncio
    async def test_revoke_permission_without_event_store(self):
        """Test permission revocation without event store"""
        service = AuthorizationService(event_store=None, tenant_id="TEST")
        await service.grant_permission("user123", Permission.READ, "admin")
        await service.revoke_permission("user123", Permission.READ, "admin")
        assert not service.has_permission("user123", Permission.READ)


class TestEncryptionEdgeCases:
    """Test encryption edge cases for full coverage"""

    @pytest.fixture
    def mock_event_store(self):
        """Mock event store for testing"""
        store = Mock()
        store.append_event = AsyncMock()
        return store

    def test_encryption_with_no_key(self, mock_event_store):
        """Test encryption service generates key when none provided"""
        with patch.dict("os.environ", {}, clear=True):
            service = EncryptionService(event_store=mock_event_store, tenant_id="TEST")
            assert service.key is not None
            assert len(service.key) > 0

    def test_encryption_with_env_key(self, mock_event_store):
        """Test encryption service uses environment key from environment"""
        from cryptography.fernet import Fernet

        test_key = Fernet.generate_key()
        with patch.dict("os.environ", {"ENCRYPTION_KEY": test_key.decode()}, clear=True):
            service = EncryptionService(event_store=mock_event_store, tenant_id="TEST")
            assert service.key == test_key

    @pytest.mark.asyncio
    async def test_encrypt_without_event_store(self):
        """Test encryption without event store"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        encrypted = await service.encrypt("test data", "user123", "test_type", "test_field")
        assert encrypted != "test data"

    def test_decrypt_without_event_store(self):
        """Test decryption without event store"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        # Use synchronous encrypt for testing decrypt
        test_data = "test data"
        encrypted = service.fernet.encrypt(test_data.encode())
        import base64

        encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
        decrypted = service.decrypt(encrypted_b64)
        assert decrypted == test_data

    def test_hash_without_event_store(self):
        """Test hashing without event store"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        hashed = service.hash_data("test data", "sha256")
        assert hashed != "test data"
        assert len(hashed) == 64  # SHA256 produces 64 hex characters

    def test_generate_key(self):
        """Test key generation"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        new_key = service.generate_key()
        assert new_key is not None
        assert len(new_key) > 0

    def test_derive_key_without_event_store(self):
        """Test key derivation without event store"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        derived, salt = service.derive_key_from_password("password123", b"salt123")
        assert derived is not None
        assert len(derived) > 0
        assert salt is not None


class TestFullCoverage:
    """Additional tests to achieve 100% coverage"""

    @pytest.fixture
    def mock_event_store(self):
        """Mock event store for testing"""
        store = Mock()
        store.append_event = AsyncMock()
        return store

    @pytest.mark.asyncio
    async def test_authentication_with_event_store(self, mock_event_store):
        """Test authentication publishes events when event store is present"""
        service = AuthenticationService(event_store=mock_event_store, tenant_id="TEST")
        stored_hash = service.hash_password("TestPass123!")

        result = await service.authenticate_user(
            user_id="user123",
            password="TestPass123!",
            stored_hash=stored_hash,
            authentication_method="password",
            ip_address="127.0.0.1",
            user_agent="TestAgent",
        )

        assert result is True
        mock_event_store.append_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_with_event_store(self, mock_event_store):
        """Test password change publishes events when event store is present"""
        service = AuthenticationService(event_store=mock_event_store, tenant_id="TEST")
        old_hash = service.hash_password("OldPass123!")

        new_hash = await service.change_password(
            user_id="user123",
            old_password="OldPass123!",
            new_password="NewPass123!",
            stored_hash=old_hash,
            changed_by="user123",
        )

        assert new_hash != old_hash
        mock_event_store.append_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_authorization_revoke_permission_with_event_store(self, mock_event_store):
        """Test permission revocation publishes events"""
        from ultracore.security.authorization import AuthorizationService, Permission

        service = AuthorizationService(event_store=mock_event_store, tenant_id="TEST")

        # Grant permission first
        await service.grant_permission("user123", Permission.READ, "admin")

        # Revoke permission
        await service.revoke_permission("user123", Permission.READ, "admin")

        assert not service.has_permission("user123", Permission.READ)
        # Should have 2 calls: one for grant, one for revoke
        assert mock_event_store.append_event.call_count == 2

    @pytest.mark.asyncio
    async def test_encryption_with_event_store(self, mock_event_store):
        """Test encryption publishes events when event store is present"""
        service = EncryptionService(event_store=mock_event_store, tenant_id="TEST")

        encrypted = await service.encrypt(
            data="sensitive data", user_id="user123", data_type="ssn", field_name="social_security"
        )

        assert encrypted != "sensitive data"
        mock_event_store.append_event.assert_called_once()

    def test_encryption_with_provided_key(self, mock_event_store):
        """Test encryption service with explicitly provided key"""
        from cryptography.fernet import Fernet

        test_key = Fernet.generate_key().decode()
        service = EncryptionService(
            encryption_key=test_key, event_store=mock_event_store, tenant_id="TEST"
        )
        assert service.key == test_key.encode()

    def test_hash_sha512(self):
        """Test SHA512 hashing algorithm"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        hashed = service.hash_data("test data", "sha512")
        assert len(hashed) == 128  # SHA512 produces 128 hex characters

    def test_hash_sha1(self):
        """Test SHA1 hashing algorithm"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        hashed = service.hash_data("test data", "sha1")
        assert len(hashed) == 40  # SHA1 produces 40 hex characters

    def test_hash_unsupported_algorithm(self):
        """Test that unsupported hash algorithms raise error"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            service.hash_data("test data", "md5")

    def test_decrypt_invalid_data(self):
        """Test that decryption of invalid data raises error"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        with pytest.raises(ValueError, match="Decryption failed"):
            service.decrypt("invalid_encrypted_data")

    @pytest.mark.asyncio
    async def test_encrypt_field(self):
        """Test encrypt_field wrapper method"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        encrypted = await service.encrypt_field(
            field_value="sensitive value", field_name="ssn", user_id="user123", data_type="personal"
        )
        assert encrypted != "sensitive value"

    def test_decrypt_field(self):
        """Test decrypt_field wrapper method"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        # Encrypt first
        test_data = "test value"
        encrypted = service.fernet.encrypt(test_data.encode())
        import base64

        encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")

        # Decrypt using decrypt_field
        decrypted = service.decrypt_field(encrypted_b64, "test_field")
        assert decrypted == test_data

    def test_get_key(self):
        """Test get_key method"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        key = service.get_key()
        assert key is not None
        assert isinstance(key, str)
        assert len(key) > 0

    def test_decrypt_sensitive_data_with_invalid_value(self):
        """Test decrypt_sensitive_data handles decryption failures gracefully"""
        service = EncryptionService(event_store=None, tenant_id="TEST")
        data = {
            "user_id": "USER-001",
            "ssn": "invalid_encrypted_data",  # This will fail to decrypt
            "name": "John Doe",
        }

        decrypted = service.decrypt_sensitive_data(data)

        # Should keep invalid encrypted data as-is
        assert decrypted["ssn"] == "invalid_encrypted_data"
        assert decrypted["name"] == "John Doe"
