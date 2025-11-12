"""MCP Tools for Fixed Deposits"""
from .server import FixedDepositMCPServer
from .tools import register_fd_tools

__all__ = ["FixedDepositMCPServer", "register_fd_tools"]
