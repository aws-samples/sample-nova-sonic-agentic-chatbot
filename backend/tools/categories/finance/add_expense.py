"""
AddExpenseTool - Records a new expense with category tracking.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState
from .models import BudgetCategory


class AddExpenseTool(BaseTool):
    """
    Tool for recording expenses with budget category tracking.
    
    Creates a transaction and updates the corresponding budget category.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "add_expense",
            "description": "Record a new expense with category tracking. Use this when the user wants to log a purchase, record spending, or track an expense. Categories include groceries, dining, transportation, utilities, entertainment, shopping, healthcare, and other.",
            "shortDescription": "Recording an expense",
            "schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the expense (e.g., 'Lunch at cafe', 'Gas station')"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount spent in USD (positive number)"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["groceries", "dining", "transportation", "utilities", 
                                "entertainment", "shopping", "healthcare", "other"],
                        "description": "Spending category for budget tracking"
                    }
                },
                "required": ["description", "amount", "category"]
            }
        }

    async def execute(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the add expense operation."""
        state = FinanceState()
        
        description = content.get("description", "")
        amount = content.get("amount", 0)
        category_str = content.get("category", "other")
        
        # Validate amount
        if amount <= 0:
            state.log_action("add_expense", f"Failed: Invalid amount ${amount}")
            
            model_result = {
                "success": False,
                "error": "invalid_amount",
                "message": "Amount must be greater than zero"
            }
            
            ui_result = {
                "type": "app",
                "appName": "finance",
                "props": {
                    "action": "error",
                    "error": {"code": "invalid_amount", "message": "Invalid amount"},
                    "state": state.get_state_snapshot()
                }
            }
            
            return self.format_response(model_result, ui_result)
        
        # Validate category
        try:
            category = BudgetCategory(category_str)
        except ValueError:
            category = BudgetCategory.OTHER
        
        # Check sufficient funds
        if amount > state.balance:
            state.log_action("add_expense", f"Failed: Insufficient funds for ${amount:.2f}")
            
            model_result = {
                "success": False,
                "error": "insufficient_funds",
                "message": f"Insufficient funds. Current balance: ${state.balance:.2f}",
                "current_balance": state.balance,
                "requested_amount": amount
            }
            
            ui_result = {
                "type": "app",
                "appName": "finance",
                "props": {
                    "action": "error",
                    "error": {"code": "insufficient_funds", "message": "Insufficient funds"},
                    "state": state.get_state_snapshot()
                }
            }
            
            return self.format_response(model_result, ui_result)
        
        # Record the expense
        transaction = state.add_transaction(
            description=description,
            amount=-amount,  # Negative for expense
            category=category
        )
        
        # Get updated budget for this category
        budget_info = None
        for budget in state.budgets:
            if budget.category == category:
                remaining = budget.limit - budget.spent
                percent_used = (budget.spent / budget.limit * 100) if budget.limit > 0 else 0
                budget_info = {
                    "category": category.value,
                    "spent": budget.spent,
                    "limit": budget.limit,
                    "remaining": remaining,
                    "percent_used": round(percent_used, 1),
                    "over_budget": budget.spent > budget.limit
                }
                break
        
        state.log_action("add_expense", f"Recorded ${amount:.2f} expense for {description}")
        
        model_result = {
            "success": True,
            "description": description,
            "amount": amount,
            "formatted_amount": f"${amount:,.2f}",
            "category": category.value,
            "new_balance": state.balance,
            "transaction_id": transaction.id,
            "budget_status": budget_info
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "expense_added",
                "transaction": {
                    "id": transaction.id,
                    "description": transaction.description,
                    "amount": transaction.amount,
                    "category": category.value,
                    "date": transaction.date.isoformat()
                },
                "budgetStatus": budget_info,
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
