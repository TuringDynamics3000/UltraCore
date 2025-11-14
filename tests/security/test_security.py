import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from ultracore.security.authentication import AuthenticationService
from ultracore.security.authorization import AuthorizationService
from ultracore.security.encryption import EncryptionService


class TestAuthentication:
    '''Test authentication security'''
    
    @pytest.fixture
    def auth_service(self):
        return AuthenticationService()
    
    def test_password_hashing(self, auth_service):
        '''Test that passwords are properly hashed'''
        password = 'SecurePassword123!'
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50
        assert auth_service.verify_password(password, hashed)
    
    def test_weak_password_rejection(self, auth_service):
        '''Test rejection of weak passwords'''
        weak_passwords = ['123456', 'password', 'abc', 'test']
        
        for weak_pwd in weak_passwords:
            with pytest.raises(ValueError, match='Password too weak'):
                auth_service.validate_password_strength(weak_pwd)
    
    def test_jwt_token_generation(self, auth_service):
        '''Test JWT token generation and validation'''
        user_data = {'user_id': 'USER-001', 'tenant_id': 'TENANT-001'}
        token = auth_service.create_access_token(user_data)
        
        assert token is not None
        assert isinstance(token, str)
        
        decoded = auth_service.verify_token(token)
        assert decoded['user_id'] == 'USER-001'
        assert decoded['tenant_id'] == 'TENANT-001'
    
    def test_expired_token_rejection(self, auth_service):
        '''Test that expired tokens are rejected'''
        with patch('time.time', return_value=0):
            token = auth_service.create_access_token(
                {'user_id': 'USER-001'},
                expires_in=1
            )
        
        with pytest.raises(HTTPException, match='Token expired'):
            auth_service.verify_token(token)
    
    def test_invalid_token_rejection(self, auth_service):
        '''Test rejection of invalid/tampered tokens'''
        invalid_tokens = [
            'invalid.token.here',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid',
            '',
            None
        ]
        
        for token in invalid_tokens:
            with pytest.raises(HTTPException):
                auth_service.verify_token(token)
    
    def test_rate_limiting(self, auth_service):
        '''Test rate limiting on authentication attempts'''
        user_id = 'USER-001'
        
        # Simulate multiple failed login attempts
        for _ in range(5):
            auth_service.record_failed_login(user_id)
        
        # Should be rate limited now
        assert auth_service.is_rate_limited(user_id) is True
    
    def test_session_management(self, auth_service):
        '''Test session creation and validation'''
        user_id = 'USER-001'
        session_id = auth_service.create_session(user_id)
        
        assert auth_service.validate_session(session_id) is True
        
        auth_service.invalidate_session(session_id)
        assert auth_service.validate_session(session_id) is False


class TestAuthorization:
    '''Test authorization and permissions'''
    
    @pytest.fixture
    def authz_service(self):
        return AuthorizationService()
    
    def test_role_based_access_control(self, authz_service):
        '''Test RBAC permissions'''
        user = {'user_id': 'USER-001', 'roles': ['client']}
        
        assert authz_service.has_permission(user, 'view_account') is True
        assert authz_service.has_permission(user, 'approve_loan') is False
    
    def test_admin_permissions(self, authz_service):
        '''Test admin has all permissions'''
        admin = {'user_id': 'ADMIN-001', 'roles': ['admin']}
        
        assert authz_service.has_permission(admin, 'view_account') is True
        assert authz_service.has_permission(admin, 'approve_loan') is True
        assert authz_service.has_permission(admin, 'delete_user') is True
    
    def test_tenant_isolation(self, authz_service):
        '''Test that users can only access their tenant data'''
        user = {'user_id': 'USER-001', 'tenant_id': 'TENANT-A'}
        
        # Can access own tenant
        assert authz_service.can_access_resource(
            user, 
            resource={'tenant_id': 'TENANT-A'}
        ) is True
        
        # Cannot access other tenant
        assert authz_service.can_access_resource(
            user,
            resource={'tenant_id': 'TENANT-B'}
        ) is False
    
    def test_permission_inheritance(self, authz_service):
        '''Test that permissions are inherited from roles'''
        user = {'user_id': 'USER-001', 'roles': ['manager', 'client']}
        
        # Should have both manager and client permissions
        assert authz_service.has_permission(user, 'view_account') is True
        assert authz_service.has_permission(user, 'approve_small_loan') is True


class TestEncryption:
    '''Test data encryption and security'''
    
    @pytest.fixture
    def encryption_service(self):
        return EncryptionService()
    
    def test_data_encryption_decryption(self, encryption_service):
        '''Test symmetric encryption/decryption'''
        sensitive_data = 'SSN: 123-45-6789'
        
        encrypted = encryption_service.encrypt(sensitive_data)
        assert encrypted != sensitive_data
        
        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == sensitive_data
    
    def test_pii_encryption(self, encryption_service):
        '''Test PII data is encrypted at rest'''
        pii_data = {
            'ssn': '123-45-6789',
            'credit_card': '4111-1111-1111-1111',
            'bank_account': '123456789'
        }
        
        encrypted_pii = encryption_service.encrypt_pii(pii_data)
        
        for key, value in encrypted_pii.items():
            assert value != pii_data[key]
            assert len(value) > len(pii_data[key])
    
    def test_field_level_encryption(self, encryption_service):
        '''Test field-level encryption for sensitive fields'''
        client_data = {
            'name': 'John Doe',  # Not encrypted
            'ssn': '123-45-6789',  # Encrypted
            'email': 'john@example.com'  # Not encrypted
        }
        
        encrypted = encryption_service.encrypt_sensitive_fields(
            client_data,
            sensitive_fields=['ssn']
        )
        
        assert encrypted['name'] == 'John Doe'
        assert encrypted['ssn'] != '123-45-6789'
        assert encrypted['email'] == 'john@example.com'


class TestSecurityHeaders:
    '''Test security headers and CORS'''
    
    def test_security_headers_present(self, client):
        '''Test that security headers are set'''
        response = client.get('/api/health')
        
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert 'X-Frame-Options' in response.headers
        assert 'Strict-Transport-Security' in response.headers
    
    def test_cors_configuration(self, client):
        '''Test CORS is properly configured'''
        response = client.options(
            '/api/accounts',
            headers={'Origin': 'https://malicious-site.com'}
         )
        
        # Should not allow arbitrary origins
        assert 'Access-Control-Allow-Origin' not in response.headers or \
               response.headers.get('Access-Control-Allow-Origin') != '*'


class TestInputValidation:
    '''Test input validation and sanitization'''
    
    def test_sql_injection_prevention(self):
        '''Test SQL injection attempts are blocked'''
        malicious_inputs = [
            \"'; DROP TABLE users; --\",
            \"1' OR '1'='1\",
            \"admin'--\",
            \"1; DELETE FROM accounts\"
        ]
        
        from ultracore.security.validation import sanitize_input
        
        for malicious in malicious_inputs:
            sanitized = sanitize_input(malicious)
            assert 'DROP' not in sanitized.upper()
            assert 'DELETE' not in sanitized.upper()
            assert '--' not in sanitized
    
    def test_xss_prevention(self):
        '''Test XSS attempts are blocked'''
        malicious_inputs = [
            '<script>alert(\"XSS\")</script>',
            '<img src=x onerror=alert(1)>',
            'javascript:alert(1)',
            '<iframe src=\"evil.com\"></iframe>'
        ]
        
        from ultracore.security.validation import sanitize_html
        
        for malicious in malicious_inputs:
            sanitized = sanitize_html(malicious)
            assert '<script>' not in sanitized.lower()
            assert 'javascript:' not in sanitized.lower()
            assert 'onerror' not in sanitized.lower()
    
    def test_amount_validation(self):
        '''Test financial amount validation'''
        from ultracore.security.validation import validate_amount
        
        # Valid amounts
        assert validate_amount('100.50') is True
        assert validate_amount('1000000.00') is True
        
        # Invalid amounts
        with pytest.raises(ValueError):
            validate_amount('-100')  # Negative
        with pytest.raises(ValueError):
            validate_amount('abc')  # Non-numeric
        with pytest.raises(ValueError):
            validate_amount('100.123')  # Too many decimals


class TestAuditLogging:
    '''Test security audit logging'''
    
    def test_sensitive_operations_logged(self):
        '''Test that sensitive operations are logged'''
        from ultracore.audit.logger import AuditLogger
        
        logger = AuditLogger()
        
        with patch.object(logger, '_write_log') as mock_log:
            logger.log_account_access(
                user_id='USER-001',
                account_id='ACC-001',
                action='view_balance'
            )
            
            mock_log.assert_called_once()
            log_entry = mock_log.call_args[0][0]
            assert log_entry['user_id'] == 'USER-001'
            assert log_entry['action'] == 'view_balance'
            assert 'timestamp' in log_entry
    
    def test_failed_login_logged(self):
        '''Test failed login attempts are logged'''
        from ultracore.audit.logger import AuditLogger
        
        logger = AuditLogger()
        
        with patch.object(logger, '_write_log') as mock_log:
            logger.log_failed_login(
                username='john@example.com',
                ip_address='192.168.1.1',
                reason='invalid_password'
            )
            
            mock_log.assert_called_once()
            log_entry = mock_log.call_args[0][0]
            assert log_entry['event_type'] == 'failed_login'
            assert log_entry['severity'] == 'warning'