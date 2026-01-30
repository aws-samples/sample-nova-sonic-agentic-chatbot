"""
SendMoneyTool - Sends money to a contact.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState


class SendMoneyTool(BaseTool):
    """
    Tool for sending money to a contact.
    
    Validates recipient exists in contacts and amount is valid,
    then deducts from balance and creates a transaction record.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "send_money",
            "description": "Send money to a contact. Requires recipient name and amount. Use this when the user wants to transfer money, pay someone, or send funds to a contact.",
            "shortDescription": "Sending money to contact",
            "schema": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "Name of the recipient (must be an existing contact)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount to send in USD (must be positive and not exceed balance)"
                    }
                },
                "required": ["recipient", "amount"]
            }
        }

    async def execute(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the send money operation."""
        state = FinanceState()
        
        recipient_name = content.get("recipient", "")
        amount = content.get("amount", 0)
        
        # Validate amount is positive
        if amount <= 0:
            state.log_action("send_money", f"Failed: Invalid amount ${amount:.2f}")
            return self._error_response(
                state, "invalid_amount", "Amount must be greater than zero",
                {"requested_amount": amount}
            )
        
        # Validate recipient exists in contacts
        contact = state.find_contact_by_name(recipient_name)
        if contact is None:
            available_contacts = state.get_contact_names()
            state.log_action("send_money", f"Failed: Unknown recipient '{recipient_name}'")
            return self._error_response(
                state, "unknown_recipient", f"Contact '{recipient_name}' not found",
                {"available_contacts": available_contacts}
            )
        
        # Validate sufficient funds
        if amount > state.balance:
            state.log_action("send_money", f"Failed: Insufficient funds for ${amount:.2f}")
            return self._error_response(
                state, "insufficient_funds",
                f"Insufficient funds. Current balance: ${state.balance:.2f}",
                {"current_balance": state.balance, "requested_amount": amount,
                 "shortfall": amount - state.balance}
            )
        
        # Execute the transfer
        transaction = state.add_transaction(
            description=f"Transfer to {contact.name}",
            amount=-amount,
            recipient=contact.name
        )
        
        state.log_action("send_money", f"Sent ${amount:.2f} to {contact.name}")
        
        model_result = {
            "success": True,
            "amount_sent": amount,
            "recipient": contact.name,
            "new_balance": state.balance,
            "currency": "USD",
            "transaction_id": transaction.id
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "money_sent",
                "transaction": {
                    "id": transaction.id,
                    "description": transaction.description,
                    "amount": transaction.amount,
                    "date": transaction.date.isoformat(),
                    "recipient": transaction.recipient
                },
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
    
    def _error_response(
        self, state: FinanceState, error_code: str, 
        message: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a standardized error response."""
        model_result = {"success": False, "error": error_code, "message": message, **details}
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "error",
                "error": {"code": error_code, "message": message},
                "state": state.get_state_snapshot()
            }
        }
        return self.format_response(model_result, ui_result)
