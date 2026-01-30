"""
REST API endpoint for finance state.
"""
from fastapi import APIRouter

from tools.categories.finance.state import FinanceState

router = APIRouter()


@router.get("/api/finance/state")
async def get_finance_state():
    """
    Get the current finance state snapshot.
    
    Returns the FinanceState including balance, savings, transactions,
    contacts, budgets, bills, goals, and action history.
    """
    state = FinanceState()
    return state.get_state_snapshot()
