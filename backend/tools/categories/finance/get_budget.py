"""
GetBudgetTool - Returns budget information and spending status.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState
from .models import BudgetCategory


class GetBudgetTool(BaseTool):
    """
    Tool for getting budget information and spending status.
    
    Returns budget limits, current spending, and remaining amounts.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "get_budget",
            "description": "Get the user's budget information including spending limits and current spending by category. Use this when the user asks about their budget, spending limits, how much they've spent, or remaining budget.",
            "shortDescription": "Getting budget status",
            "schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["groceries", "dining", "transportation", "utilities", 
                                "entertainment", "shopping", "healthcare", "other", "all"],
                        "description": "Budget category to check (defaults to all)"
                    }
                },
                "required": []
            }
        }

    async def execute(self, content: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the get budget operation."""
        state = FinanceState()
        content = content or {}
        category_filter = content.get("category", "all")
        
        state.log_action("get_budget", f"Retrieved budget for {category_filter}")
        
        budgets = state.budgets
        
        # Filter by category if specified
        if category_filter != "all":
            try:
                cat = BudgetCategory(category_filter)
                budgets = [b for b in budgets if b.category == cat]
            except ValueError:
                pass
        
        # Format budget data
        formatted_budgets = []
        total_limit = 0
        total_spent = 0
        
        for budget in budgets:
            remaining = budget.limit - budget.spent
            percent_used = (budget.spent / budget.limit * 100) if budget.limit > 0 else 0
            status = "on_track" if percent_used < 80 else ("warning" if percent_used < 100 else "over_budget")
            
            formatted_budgets.append({
                "category": budget.category.value,
                "limit": budget.limit,
                "formatted_limit": f"${budget.limit:,.2f}",
                "spent": budget.spent,
                "formatted_spent": f"${budget.spent:,.2f}",
                "remaining": remaining,
                "formatted_remaining": f"${remaining:,.2f}",
                "percent_used": round(percent_used, 1),
                "status": status
            })
            
            total_limit += budget.limit
            total_spent += budget.spent
        
        total_remaining = total_limit - total_spent
        
        model_result = {
            "budgets": formatted_budgets,
            "count": len(formatted_budgets),
            "total_limit": total_limit,
            "total_spent": total_spent,
            "total_remaining": total_remaining,
            "formatted_total_remaining": f"${total_remaining:,.2f}",
            "currency": "USD"
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "show_budget",
                "category": category_filter,
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
