"""
Client Domain API
"""
from fastapi import APIRouter, HTTPException
import uuid
from typing import Dict

from ultracore.domains.client.aggregate import (
    ClientAggregate, OnboardingRequest, KYCDocumentRequest
)
from ultracore.domains.client.kyc_service import kyc_service
from ultracore.infrastructure.event_store.store import get_event_store

router = APIRouter()


@router.post('/')
async def onboard_client(request: OnboardingRequest):
    '''
    Onboard a new customer
    
    Creates client profile and starts KYC process
    '''
    client_id = f'CLIENT-{str(uuid.uuid4())[:8]}'
    
    client = ClientAggregate(client_id)
    await client.onboard(request)
    
    return {
        'client_id': client_id,
        'status': client.status.value,
        'kyc_status': client.kyc_status.value,
        'message': 'Client onboarded successfully. Please submit KYC documents.',
        'next_step': f'/api/v1/clients/{client_id}/kyc/documents'
    }


@router.get('/{client_id}')
async def get_client(client_id: str):
    '''Get client profile'''
    client = ClientAggregate(client_id)
    await client.load_from_events()
    
    if not client.first_name:
        raise HTTPException(status_code=404, detail='Client not found')
    
    return {
        'client_id': client.client_id,
        'name': f'{client.first_name} {client.last_name}',
        'email': client.email,
        'status': client.status.value,
        'kyc_status': client.kyc_status.value,
        'risk_score': client.risk_score
    }


@router.post('/{client_id}/kyc/documents')
async def submit_kyc_document(client_id: str, document: KYCDocumentRequest):
    '''
    Submit KYC identity document
    
    Accepts: Passport, Driver's License, Medicare Card
    '''
    client = ClientAggregate(client_id)
    await client.load_from_events()
    
    if not client.first_name:
        raise HTTPException(status_code=404, detail='Client not found')
    
    await client.submit_kyc_document(document)
    
    return {
        'client_id': client_id,
        'kyc_status': client.kyc_status.value,
        'message': 'Document submitted successfully',
        'next_step': f'/api/v1/clients/{client_id}/kyc/verify'
    }


@router.post('/{client_id}/kyc/verify')
async def verify_kyc(client_id: str):
    '''
    AI-powered KYC verification
    
    Performs:
    - Identity verification
    - AML/CTF compliance checks
    - Risk assessment
    - Age verification
    '''
    client = ClientAggregate(client_id)
    await client.load_from_events()
    
    if not client.first_name:
        raise HTTPException(status_code=404, detail='Client not found')
    
    if client.kyc_status != 'IN_PROGRESS':
        raise HTTPException(status_code=400, detail='No KYC documents submitted')
    
    # Get client data from events
    store = get_event_store()
    events = await store.get_events(client_id)
    
    client_data = {}
    document_data = {}
    
    for event in events:
        if event.event_type == 'ClientOnboarded':
            client_data = event.event_data
        elif event.event_type == 'KYCDocumentSubmitted':
            document_data = event.event_data
    
    # AI verification
    verification_result = await kyc_service.verify_identity(client_data, document_data)
    
    # Update client based on verification
    await client.verify_kyc(verification_result)
    
    return {
        'client_id': client_id,
        'kyc_status': client.kyc_status.value,
        'client_status': client.status.value,
        'risk_score': verification_result['risk_score'],
        'risk_level': verification_result['risk_level'],
        'verification': verification_result
    }


@router.get('/{client_id}/360')
async def get_customer_360(client_id: str):
    '''
    Customer 360 View
    
    Complete customer profile with all history
    '''
    store = get_event_store()
    events = await store.get_events(client_id)
    
    if not events:
        raise HTTPException(status_code=404, detail='Client not found')
    
    client = ClientAggregate(client_id)
    await client.load_from_events()
    
    # Build 360 view
    profile = {}
    kyc_documents = []
    timeline = []
    
    for event in events:
        timeline.append({
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type,
            'user': event.user_id
        })
        
        if event.event_type == 'ClientOnboarded':
            profile = event.event_data
        elif event.event_type == 'KYCDocumentSubmitted':
            kyc_documents.append(event.event_data)
    
    return {
        'client_id': client_id,
        'profile': profile,
        'status': client.status.value,
        'kyc_status': client.kyc_status.value,
        'risk_score': client.risk_score,
        'kyc_documents': kyc_documents,
        'timeline': timeline,
        'total_events': len(events)
    }


@router.get('/{client_id}/events')
async def get_client_events(client_id: str):
    '''Get all events for a client'''
    store = get_event_store()
    events = await store.get_events(client_id)
    
    return {
        'client_id': client_id,
        'events': [event.to_dict() for event in events]
    }
