"""
REST API endpoint for banking state.
"""
from fastapi import APIRouter

from tools.categories.banking.state import BankingState

router = APIRouter()


@router.get("/api/banking/state")
async def get_banking_state():
    """
    Get the current banking state snapshot.
    
    Returns the initial BankingState including balance, transactions,
    contacts, and action history.
    
    Requirements: 7.1, 7.2, 7.3
    """
    state = BankingState()
    return state.get_state_snapshot()
