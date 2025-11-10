"""
MCP (Model Context Protocol) API
Enables AI agents to interact with banking system
"""
from fastapi import APIRouter
from ultracore.agentic_ai.mcp_server import mcp_server

router = APIRouter()


@router.get('/mcp/tools')
async def list_mcp_tools():
    '''
    List available tools for AI agents
    
    MCP standard interface
    '''
    return {
        'tools': mcp_server.list_tools(),
        'protocol': 'MCP/1.0',
        'server': 'UltraCore Banking'
    }


@router.get('/mcp/resources')
async def list_mcp_resources():
    '''
    List accessible data resources
    
    MCP standard interface
    '''
    return {
        'resources': mcp_server.list_resources(),
        'protocol': 'MCP/1.0',
        'server': 'UltraCore Banking'
    }


@router.get('/mcp/capabilities')
async def get_mcp_capabilities():
    '''
    Get AI agent capabilities
    '''
    return {
        'protocol': 'MCP/1.0',
        'server_name': 'UltraCore Banking AI',
        'server_version': '2.0.0',
        'capabilities': {
            'tools': True,
            'resources': True,
            'prompts': True,
            'logging': True
        },
        'features': [
            'Customer 360 Access',
            'Loan Eligibility Checking',
            'Credit Risk Analysis',
            'Fraud Detection',
            'General Ledger Queries',
            'Compliance Checking'
        ]
    }
