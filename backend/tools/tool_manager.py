import json
from typing import Dict, Any, List
from .base import ToolRegistry
from .categories.finance import (
    CheckBalanceTool,
    SendMoneyTool,
    GetTransactionsTool,
    GetStockQuoteTool,
    GetBudgetTool,
    PayBillTool,
    GetFinancialGoalsTool,
    AddExpenseTool,
    BuyStockTool,
    GetPortfolioTool,
)


class ToolManager:
    def __init__(self):
        self.registry = ToolRegistry()
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        """Initialize the tool registry with all available financial tools"""
        self.registry.register_tools([
            # Account tools
            CheckBalanceTool(),
            SendMoneyTool(),
            GetTransactionsTool(),
            
            # Budget & expense tools
            GetBudgetTool(),
            AddExpenseTool(),
            
            # Bills & payments
            PayBillTool(),
            
            # Investments
            GetStockQuoteTool(),
            BuyStockTool(),
            GetPortfolioTool(),
            
            # Goals & planning
            GetFinancialGoalsTool(),
        ])

    async def execute_tool(self, tool_name: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name"""
        try:
            return await self.registry.execute_tool(tool_name, content)
        except KeyError:
            raise KeyError(f"Tool '{tool_name}' not found")

    def get_tool_configs(self) -> List[Dict[str, Any]]:
        """Get all tool configurations formatted for Nova Sonic"""
        configs = self.registry.get_tool_configs()
        return [
            {
                "toolSpec": {
                    "name": config["name"],
                    "description": config["description"],
                    "inputSchema": {
                        "json": json.dumps(config["schema"])
                    }
                }
            }
            for config in configs
        ]
