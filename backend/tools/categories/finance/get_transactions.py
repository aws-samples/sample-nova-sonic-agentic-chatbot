"""
GetTransactionsTool - Returns the user's transaction history.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState
from .models import BudgetCategory


class GetTransactionsTool(BaseTool):
    """
    Tool for retrieving the user's transaction history.
    
    Returns transactions with optional filtering by category or type.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "get_transactions",
            "description": "Get the user's recent transaction history. Use this when the user asks about their transactions, spending, recent activity, or payment history. Can filter by category or transaction type.",
            "shortDescription": "Getting transaction history",
            "schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of transactions to return (optional)"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["groceries", "dining", "transportation", "utilities", 
                                "entertainment", "shopping", "healthcare", "other"],
                        "description": "Filter by spending category (optional)"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["incoming", "outgoing", "all"],
                        "description": "Filter by transaction type (optional, defaults to all)"
                    }
                },
                "required": []
            }
        }

    async def execute(self, content: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the get transactions operation."""
        state = FinanceState()
        content = content or {}
        
        state.log_action("get_transactions", "Retrieved transaction history")
        
        transactions = state.transactions.copy()
        
        # Filter by category if specified
        category_filter = content.get("category")
        if category_filter:
            try:
                cat = BudgetCategory(category_filter)
                transactions = [t for t in transactions if t.category == cat]
            except ValueError:
                pass
        
        # Filter by type if specified
        type_filter = content.get("type", "all")
        if type_filter == "incoming":
            transactions = [t for t in transactions if t.amount > 0]
        elif type_filter == "outgoing":
            transactions = [t for t in transactions if t.amount < 0]
        
        # Apply limit
        limit = content.get("limit")
        if limit is not None and isinstance(limit, int) and limit > 0:
            transactions = transactions[-limit:]
        
        # Format transactions
        formatted_transactions = [
            {
                "id": t.id,
                "description": t.description,
                "amount": t.amount,
                "formatted_amount": f"${abs(t.amount):,.2f}",
                "type": "incoming" if t.amount > 0 else "outgoing",
                "date": t.date.isoformat(),
                "recipient": t.recipient,
                "category": t.category.value if t.category else None
            }
            for t in transactions
        ]
        
        total_incoming = sum(t.amount for t in transactions if t.amount > 0)
        total_outgoing = sum(abs(t.amount) for t in transactions if t.amount < 0)
        
        model_result = {
            "transactions": formatted_transactions,
            "count": len(formatted_transactions),
            "total_incoming": total_incoming,
            "total_outgoing": total_outgoing,
            "net_flow": total_incoming - total_outgoing,
            "currency": "USD"
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "show_transactions",
                "filters": {"category": category_filter, "type": type_filter},
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
