"""
GetPortfolioTool - Returns the user's investment portfolio.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState


class GetPortfolioTool(BaseTool):
    """
    Tool for getting the user's investment portfolio.
    
    Returns all holdings with current values and gains/losses.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "get_portfolio",
            "description": "Get the user's investment portfolio showing all stock holdings, current values, and gains/losses. Use this when the user asks about their investments, portfolio, holdings, or how their stocks are doing.",
            "shortDescription": "Getting investment portfolio",
            "schema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Optional: specific stock symbol to check (returns all if not specified)"
                    }
                },
                "required": []
            }
        }

    async def execute(self, content: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the get portfolio operation."""
        state = FinanceState()
        content = content or {}
        symbol_filter = content.get("symbol", "").upper() if content.get("symbol") else None
        
        state.log_action("get_portfolio", "Retrieved investment portfolio")
        
        holdings = state.portfolio
        
        # Filter by symbol if specified
        if symbol_filter:
            holdings = [h for h in holdings if h.symbol == symbol_filter]
        
        # Calculate current values and gains
        formatted_holdings = []
        total_invested = 0
        total_current_value = 0
        
        for holding in holdings:
            stock = state.get_stock(holding.symbol)
            if stock:
                current_price = stock.price
                current_value = holding.shares * current_price
                cost_basis = holding.shares * holding.average_cost
                gain_loss = current_value - cost_basis
                gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                formatted_holdings.append({
                    "symbol": holding.symbol,
                    "company_name": stock.name,
                    "shares": holding.shares,
                    "average_cost": holding.average_cost,
                    "current_price": current_price,
                    "cost_basis": cost_basis,
                    "current_value": current_value,
                    "gain_loss": gain_loss,
                    "gain_loss_percent": round(gain_loss_percent, 2),
                    "formatted_value": f"${current_value:,.2f}",
                    "formatted_gain": f"${gain_loss:+,.2f}",
                    "is_profit": gain_loss >= 0
                })
                
                total_invested += cost_basis
                total_current_value += current_value
        
        total_gain_loss = total_current_value - total_invested
        total_gain_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        model_result = {
            "holdings": formatted_holdings,
            "count": len(formatted_holdings),
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_percent": round(total_gain_percent, 2),
            "formatted_total_value": f"${total_current_value:,.2f}",
            "formatted_total_gain": f"${total_gain_loss:+,.2f}",
            "currency": "USD"
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "show_portfolio",
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
