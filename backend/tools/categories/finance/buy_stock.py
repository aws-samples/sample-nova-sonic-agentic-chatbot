"""
BuyStockTool - Simulates buying stocks.
"""
from typing import Dict, Any
from datetime import datetime
from ...base.tool import BaseTool
from .state import FinanceState


class BuyStockTool(BaseTool):
    """
    Tool for buying stocks (simulated).
    
    Validates stock exists, checks sufficient funds, and executes purchase.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "buy_stock",
            "description": "Buy shares of a stock. Use this when the user wants to invest, buy stocks, or purchase shares. Requires stock symbol and either number of shares or dollar amount. Available stocks: AAPL, GOOGL, MSFT, AMZN, TSLA.",
            "shortDescription": "Buying stock",
            "schema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)"
                    },
                    "shares": {
                        "type": "number",
                        "description": "Number of shares to buy (optional if amount is provided)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Dollar amount to invest (optional if shares is provided)"
                    }
                },
                "required": ["symbol"]
            }
        }

    async def execute(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the buy stock operation."""
        state = FinanceState()
        symbol = content.get("symbol", "").upper()
        shares = content.get("shares")
        amount = content.get("amount")
        
        # Get stock info
        stock = state.get_stock(symbol)
        
        if stock is None:
            available_symbols = list(state.stocks.keys())
            state.log_action("buy_stock", f"Stock {symbol} not found")
            
            model_result = {
                "success": False,
                "error": "symbol_not_found",
                "message": f"Stock symbol '{symbol}' not available for trading",
                "available_symbols": available_symbols
            }
            
            ui_result = {
                "type": "app",
                "appName": "finance",
                "props": {
                    "action": "error",
                    "error": {"code": "symbol_not_found", "message": f"Stock {symbol} not found"},
                    "state": state.get_state_snapshot()
                }
            }
            
            return self.format_response(model_result, ui_result)
        
        # Calculate shares and total cost
        if shares is not None and shares > 0:
            num_shares = shares
            total_cost = num_shares * stock.price
        elif amount is not None and amount > 0:
            num_shares = round(amount / stock.price, 4)
            total_cost = amount
        else:
            state.log_action("buy_stock", "Failed: No shares or amount specified")
            
            model_result = {
                "success": False,
                "error": "invalid_input",
                "message": "Please specify either number of shares or dollar amount to invest"
            }
            
            ui_result = {
                "type": "app",
                "appName": "finance",
                "props": {
                    "action": "error",
                    "error": {"code": "invalid_input", "message": "Specify shares or amount"},
                    "state": state.get_state_snapshot()
                }
            }
            
            return self.format_response(model_result, ui_result)
        
        # Check sufficient funds
        if total_cost > state.balance:
            state.log_action("buy_stock", f"Insufficient funds for ${total_cost:.2f}")
            
            model_result = {
                "success": False,
                "error": "insufficient_funds",
                "message": f"Insufficient funds. Need ${total_cost:.2f}, have ${state.balance:.2f}",
                "required": total_cost,
                "available": state.balance
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
        
        # Execute purchase
        transaction = state.add_transaction(
            description=f"Buy {num_shares} shares of {symbol}",
            amount=-total_cost,
            recipient=f"{symbol} Investment"
        )
        
        # Add to portfolio
        state.add_to_portfolio(symbol, num_shares, stock.price)
        
        state.log_action("buy_stock", f"Bought {num_shares} shares of {symbol} for ${total_cost:.2f}")
        
        model_result = {
            "success": True,
            "symbol": symbol,
            "company_name": stock.name,
            "shares_purchased": num_shares,
            "price_per_share": stock.price,
            "total_cost": total_cost,
            "formatted_cost": f"${total_cost:,.2f}",
            "new_balance": state.balance,
            "transaction_id": transaction.id
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "stock_purchased",
                "purchase": {
                    "symbol": symbol,
                    "shares": num_shares,
                    "price": stock.price,
                    "total": total_cost
                },
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
