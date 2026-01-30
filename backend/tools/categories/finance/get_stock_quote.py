"""
GetStockQuoteTool - Returns stock price information.
"""
from typing import Dict, Any
from ...base.tool import BaseTool
from .state import FinanceState


class GetStockQuoteTool(BaseTool):
    """
    Tool for getting stock price quotes.
    
    Returns current price, change, and percentage change for a stock symbol.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "get_stock_quote",
            "description": "Get the current stock price and market data for a given stock symbol. Use this when the user asks about stock prices, market performance, or wants to check their investments. Supports major stocks like AAPL, GOOGL, MSFT, AMZN, TSLA.",
            "shortDescription": "Getting stock quote",
            "schema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)"
                    }
                },
                "required": ["symbol"]
            }
        }

    async def execute(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the get stock quote operation."""
        state = FinanceState()
        symbol = content.get("symbol", "").upper()
        
        stock = state.get_stock(symbol)
        
        if stock is None:
            state.log_action("get_stock_quote", f"Stock {symbol} not found")
            available_symbols = list(state.stocks.keys())
            
            model_result = {
                "success": False,
                "error": "symbol_not_found",
                "message": f"Stock symbol '{symbol}' not found in watchlist",
                "available_symbols": available_symbols
            }
            
            ui_result = {
                "type": "app",
                "appName": "finance",
                "props": {
                    "action": "stock_not_found",
                    "symbol": symbol,
                    "state": state.get_state_snapshot()
                }
            }
            
            return self.format_response(model_result, ui_result)
        
        state.log_action("get_stock_quote", f"Retrieved quote for {symbol}")
        
        direction = "up" if stock.change >= 0 else "down"
        
        model_result = {
            "success": True,
            "symbol": stock.symbol,
            "company_name": stock.name,
            "price": stock.price,
            "formatted_price": f"${stock.price:,.2f}",
            "change": stock.change,
            "formatted_change": f"${abs(stock.change):,.2f}",
            "change_percent": stock.change_percent,
            "formatted_percent": f"{abs(stock.change_percent):.2f}%",
            "direction": direction,
            "last_updated": stock.last_updated.isoformat()
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "show_stock_quote",
                "stock": {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "price": stock.price,
                    "change": stock.change,
                    "changePercent": stock.change_percent
                },
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
