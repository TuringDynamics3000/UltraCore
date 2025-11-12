"""Fixed Deposits Commands (CQRS)"""
from .lifecycle import (
    SubmitFixedDepositApplicationCommand,
    ApproveFixedDepositCommand,
    RejectFixedDepositCommand,
    ActivateFixedDepositCommand,
    RequestPrematureClosureCommand,
    ProcessMaturityCommand
)

__all__ = [
    "SubmitFixedDepositApplicationCommand",
    "ApproveFixedDepositCommand",
    "RejectFixedDepositCommand",
    "ActivateFixedDepositCommand",
    "RequestPrematureClosureCommand",
    "ProcessMaturityCommand",
]
