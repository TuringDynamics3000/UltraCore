import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from ultracore.agentic_ai.agents.client_management.kyc_agent import KYCAgent
from ultracore.client_management.models import Client, KYCStatus
from ultracore.event_sourcing.events import KYCVerificationCompleted, KYCVerificationFailed


class TestKYCAgent:
    '''Comprehensive tests for KYC Agent'''
    
    @pytest.fixture
    def kyc_agent(self):
        '''Create KYC agent instance for testing'''
        return KYCAgent(
            tenant_id='test-tenant',
            config={'verification_threshold': 0.8}
        )
    
    @pytest.fixture
    def sample_client(self):
        '''Sample client data for testing'''
        return Client(
            client_id='CLIENT-001',
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            date_of_birth='1990-01-01',
            address='123 Main St, City, Country',
            kyc_status=KYCStatus.PENDING
        )
    
    @pytest.mark.asyncio
    async def test_verify_identity_success(self, kyc_agent, sample_client):
        '''Test successful identity verification'''
        # Arrange
        with patch.object(kyc_agent, '_verify_document') as mock_verify:
            mock_verify.return_value = {'verified': True, 'confidence': 0.95}
            
            # Act
            result = await kyc_agent.verify_identity(
                client=sample_client,
                document_type='passport',
                document_data={'number': 'AB123456'}
            )
            
            # Assert
            assert result['status'] == 'verified'
            assert result['confidence'] >= 0.8
            mock_verify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_identity_failure_low_confidence(self, kyc_agent, sample_client):
        '''Test identity verification failure due to low confidence'''
        # Arrange
        with patch.object(kyc_agent, '_verify_document') as mock_verify:
            mock_verify.return_value = {'verified': False, 'confidence': 0.5}
            
            # Act
            result = await kyc_agent.verify_identity(
                client=sample_client,
                document_type='passport',
                document_data={'number': 'AB123456'}
            )
            
            # Assert
            assert result['status'] == 'failed'
            assert result['confidence'] < 0.8
            assert 'reason' in result
    
    @pytest.mark.asyncio
    async def test_verify_address(self, kyc_agent, sample_client):
        '''Test address verification'''
        # Arrange
        with patch.object(kyc_agent, '_verify_address_document') as mock_verify:
            mock_verify.return_value = {'verified': True, 'match_score': 0.92}
            
            # Act
            result = await kyc_agent.verify_address(
                client=sample_client,
                document_type='utility_bill',
                document_data={'address': '123 Main St'}
            )
            
            # Assert
            assert result['verified'] is True
            assert result['match_score'] > 0.9
    
    @pytest.mark.asyncio
    async def test_perform_aml_check(self, kyc_agent, sample_client):
        '''Test Anti-Money Laundering (AML) check'''
        # Arrange
        with patch.object(kyc_agent, '_check_sanctions_list') as mock_sanctions, \
             patch.object(kyc_agent, '_check_pep_list') as mock_pep:
            mock_sanctions.return_value = {'found': False}
            mock_pep.return_value = {'is_pep': False}
            
            # Act
            result = await kyc_agent.perform_aml_check(sample_client)
            
            # Assert
            assert result['passed'] is True
            assert result['sanctions_check']['found'] is False
            assert result['pep_check']['is_pep'] is False
    
    @pytest.mark.asyncio
    async def test_perform_aml_check_sanctions_hit(self, kyc_agent, sample_client):
        '''Test AML check with sanctions list match'''
        # Arrange
        with patch.object(kyc_agent, '_check_sanctions_list') as mock_sanctions:
            mock_sanctions.return_value = {
                'found': True,
                'list': 'OFAC',
                'match_score': 0.95
            }
            
            # Act
            result = await kyc_agent.perform_aml_check(sample_client)
            
            # Assert
            assert result['passed'] is False
            assert result['sanctions_check']['found'] is True
            assert result['requires_manual_review'] is True
    
    @pytest.mark.asyncio
    async def test_complete_kyc_workflow(self, kyc_agent, sample_client):
        '''Test complete KYC workflow from start to finish'''
        # Arrange
        with patch.object(kyc_agent, 'verify_identity') as mock_identity, \
             patch.object(kyc_agent, 'verify_address') as mock_address, \
             patch.object(kyc_agent, 'perform_aml_check') as mock_aml, \
             patch.object(kyc_agent, '_publish_event') as mock_publish:
            
            mock_identity.return_value = {'status': 'verified', 'confidence': 0.95}
            mock_address.return_value = {'verified': True, 'match_score': 0.92}
            mock_aml.return_value = {'passed': True}
            
            # Act
            result = await kyc_agent.complete_kyc_workflow(sample_client)
            
            # Assert
            assert result['overall_status'] == 'approved'
            assert result['identity_verified'] is True
            assert result['address_verified'] is True
            assert result['aml_passed'] is True
            mock_publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_risk_scoring(self, kyc_agent, sample_client):
        '''Test risk scoring calculation'''
        # Arrange
        kyc_data = {
            'identity_confidence': 0.95,
            'address_verified': True,
            'aml_passed': True,
            'document_quality': 0.9
        }
        
        # Act
        risk_score = await kyc_agent.calculate_risk_score(sample_client, kyc_data)
        
        # Assert
        assert 0 <= risk_score <= 100
        assert risk_score < 30  # Low risk for good data
    
    @pytest.mark.asyncio
    async def test_event_publishing(self, kyc_agent, sample_client):
        '''Test that KYC events are published correctly'''
        # Arrange
        with patch.object(kyc_agent, '_event_store') as mock_store:
            mock_store.publish = AsyncMock()
            
            # Act
            await kyc_agent._publish_kyc_completed_event(
                client=sample_client,
                verification_result={'status': 'approved'}
            )
            
            # Assert
            mock_store.publish.assert_called_once()
            call_args = mock_store.publish.call_args[0][0]
            assert isinstance(call_args, KYCVerificationCompleted)
            assert call_args.client_id == sample_client.client_id
    
    def test_kyc_agent_initialization(self):
        '''Test KYC agent initialization with config'''
        # Act
        agent = KYCAgent(
            tenant_id='test-tenant',
            config={
                'verification_threshold': 0.85,
                'aml_provider': 'ComplyAdvantage'
            }
        )
        
        # Assert
        assert agent.tenant_id == 'test-tenant'
        assert agent.config['verification_threshold'] == 0.85
        assert agent.config['aml_provider'] == 'ComplyAdvantage'
    
    @pytest.mark.asyncio
    async def test_document_expiry_check(self, kyc_agent, sample_client):
        '''Test document expiry validation'''
        # Arrange
        expired_document = {
            'type': 'passport',
            'expiry_date': '2020-01-01'  # Expired
        }
        
        # Act
        result = await kyc_agent._check_document_validity(expired_document)
        
        # Assert
        assert result['valid'] is False
        assert 'expired' in result['reason'].lower()
    
    @pytest.mark.asyncio
    async def test_multi_tenant_isolation(self, sample_client):
        '''Test that KYC agents are properly isolated by tenant'''
        # Arrange
        agent1 = KYCAgent(tenant_id='tenant-1')
        agent2 = KYCAgent(tenant_id='tenant-2')
        
        # Act & Assert
        assert agent1.tenant_id != agent2.tenant_id
        assert agent1._get_tenant_config() != agent2._get_tenant_config()