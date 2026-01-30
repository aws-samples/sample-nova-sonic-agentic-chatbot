"""
GetFinancialGoalsTool - Returns financial goals and progress.
"""
from typing import Dict, Any
from datetime import date
from ...base.tool import BaseTool
from .state import FinanceState


class GetFinancialGoalsTool(BaseTool):
    """
    Tool for getting financial goals and savings progress.
    
    Returns goal targets, current progress, and projected completion.
    """
    
    def __init__(self):
        super().__init__()
        self.config = {
            "name": "get_financial_goals",
            "description": "Get the user's financial goals and savings progress. Use this when the user asks about their savings goals, financial targets, how close they are to their goals, or wants to check progress on emergency fund, vacation fund, or other savings goals.",
            "shortDescription": "Getting financial goals",
            "schema": {
                "type": "object",
                "properties": {
                    "goal_name": {
                        "type": "string",
                        "description": "Specific goal name to check (optional, returns all if not specified)"
                    }
                },
                "required": []
            }
        }

    async def execute(self, content: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the get financial goals operation."""
        state = FinanceState()
        content = content or {}
        goal_name_filter = content.get("goal_name")
        
        state.log_action("get_financial_goals", "Retrieved financial goals")
        
        goals = state.goals
        
        # Filter by goal name if specified
        if goal_name_filter:
            name_lower = goal_name_filter.lower()
            goals = [g for g in goals if name_lower in g.name.lower()]
        
        # Format goals
        formatted_goals = []
        total_target = 0
        total_saved = 0
        
        today = date.today()
        
        for goal in goals:
            remaining = goal.target_amount - goal.current_amount
            percent_complete = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            
            # Calculate days remaining if target date exists
            days_remaining = None
            on_track = None
            if goal.target_date:
                days_remaining = (goal.target_date - today).days
                if days_remaining > 0 and remaining > 0:
                    required_daily = remaining / days_remaining
                    # Assume ~$500/month savings capacity for on_track calculation
                    monthly_capacity = 500
                    on_track = (required_daily * 30) <= monthly_capacity
            
            formatted_goals.append({
                "name": goal.name,
                "description": goal.description,
                "target_amount": goal.target_amount,
                "formatted_target": f"${goal.target_amount:,.2f}",
                "current_amount": goal.current_amount,
                "formatted_current": f"${goal.current_amount:,.2f}",
                "remaining": remaining,
                "formatted_remaining": f"${remaining:,.2f}",
                "percent_complete": round(percent_complete, 1),
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "days_remaining": days_remaining,
                "on_track": on_track
            })
            
            total_target += goal.target_amount
            total_saved += goal.current_amount
        
        total_remaining = total_target - total_saved
        overall_percent = (total_saved / total_target * 100) if total_target > 0 else 0
        
        model_result = {
            "goals": formatted_goals,
            "count": len(formatted_goals),
            "total_target": total_target,
            "total_saved": total_saved,
            "total_remaining": total_remaining,
            "formatted_total_remaining": f"${total_remaining:,.2f}",
            "overall_percent_complete": round(overall_percent, 1),
            "currency": "USD"
        }
        
        ui_result = {
            "type": "app",
            "appName": "finance",
            "props": {
                "action": "show_goals",
                "goalFilter": goal_name_filter,
                "state": state.get_state_snapshot()
            }
        }
        
        return self.format_response(model_result, ui_result)
