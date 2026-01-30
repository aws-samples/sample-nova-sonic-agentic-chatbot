"""
PayBillTool - Pays a pending bill.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState
from .models import BillStatus


class PayBillTool(BaseTool):
    """
    Tool for paying pending bills.
    
    Validates bill exists and is not already paid, then processes payment.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "pay_bill",
            "description": "Pay a pending bill. Use this when the user wants to pay a bill, make a bill payment, or settle an outstanding payment. Available bills include Rent, Internet, Car Insurance, and Phone Bill.",
            "shortDescription": "Paying a bill",
            "schema": {
                "type": "object",
                "properties": {
                    "bill_name": {
                        "type": "string",
                        "description": "Name of the bill to pay (e.g., 'Rent', 'Internet', 'Phone Bill')"
                    }
                },
                "required": ["bill_name"]
            }
        }

    async def execute(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pay bill operation."""
        state = FinanceState()
        bill_name = content.get("bill_name", "")
        
        # Find the bill
        bill = state.get_bill_by_name(bill_name)
        
        if bill is None:
            available_bills = [b.name for b in state.bills if b.status != BillStatus.PAID]
            state.log_action("pay_bill", f"Bill '{bill_name}' not found")
            
            model_result = {
                "success": False,
                "error": "bill_not_found",
                "message": f"Bill '{bill_name}' not found",
                "available_bills": available_bills
            }
            
            ui_result = {
                "type": "app",
                "appName": "finance",
                "props": {
                    "action": "error",
                    "error": {"code": "bill_not_found", "message": f"Bill '{bill_name}' not found"},
                    "state": state.get_state_snapshot()
                }
            }
            
            return self.format_response(model_result, ui_result)
        
        # Check if already paid
        if bill.status == BillStatus.PAID:
            state.log_action("pay_bill", f"Bill '{bill.name}' already paid")
            
            model_result = {
                "success": False,
                "error": "already_paid",
                "message": f"Bill '{bill.name}' has already been paid"
            }
            
            ui_result = {
                "type": "app",
                "appName": "finance",
                "props": {
                    "action": "error",
                    "error": {"code": "already_paid", "message": f"Bill already paid"},
                    "state": state.get_state_snapshot()
                }
            }
            
            return self.format_response(model_result, ui_result)
        
        # Check sufficient funds
        if bill.amount > state.balance:
            state.log_action("pay_bill", f"Insufficient funds for {bill.name}")
            
            model_result = {
                "success": False,
                "error": "insufficient_funds",
                "message": f"Insufficient funds. Bill amount: ${bill.amount:.2f}, Balance: ${state.balance:.2f}",
                "bill_amount": bill.amount,
                "current_balance": state.balance
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
        
        # Process payment
        was_overdue = bill.status == BillStatus.OVERDUE
        transaction = state.pay_bill(bill)
        
        state.log_action("pay_bill", f"Paid {bill.name} - ${bill.amount:.2f}")
        
        model_result = {
            "success": True,
            "bill_name": bill.name,
            "amount_paid": bill.amount,
            "formatted_amount": f"${bill.amount:,.2f}",
            "new_balance": state.balance,
            "was_overdue": was_overdue,
            "transaction_id": transaction.id
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "bill_paid",
                "bill": {
                    "id": bill.id,
                    "name": bill.name,
                    "amount": bill.amount,
                    "wasOverdue": was_overdue
                },
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
