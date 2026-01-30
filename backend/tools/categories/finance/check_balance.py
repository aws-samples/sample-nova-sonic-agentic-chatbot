"""
CheckBalanceTool - Returns the user's current account balances.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState


class CheckBalanceTool(BaseTool):
    """
    Tool for checking the user's current account balances.
    
    Returns checking and savings balances to the model for verbal response.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "check_balance",
            "description": "Check the user's current account balances including checking and savings. Use this when the user asks about their balance, how much money they have, or their account status.",
            "shortDescription": "Checking account balances",
            "schema": {
                "type": "object",
                "properties": {
                    "account_type": {
                        "type": "string",
                        "enum": ["checking", "savings", "all"],
                        "description": "Which account balance to check (defaults to all)"
                    }
                },
                "required": []
            }
        }

    async def execute(self, content: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the check balance operation."""
        state = FinanceState()
        content = content or {}
        account_type = content.get("account_type", "all")
        
        state.log_action("check_balance", f"Checked {account_type} balance")
        
        model_result = {"currency": "USD"}
        
        if account_type in ["checking", "all"]:
            model_result["checking_balance"] = state.balance
            model_result["formatted_checking"] = f"${state.balance:,.2f}"
        
        if account_type in ["savings", "all"]:
            model_result["savings_balance"] = state.savings_balance
            model_result["formatted_savings"] = f"${state.savings_balance:,.2f}"
        
        if account_type == "all":
            total = state.balance + state.savings_balance
            model_result["total_balance"] = total
            model_result["formatted_total"] = f"${total:,.2f}"
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "highlight_balance",
                "accountType": account_type,
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
