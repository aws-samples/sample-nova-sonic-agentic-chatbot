"""
Data models for the Financial Assistant.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class BudgetCategory(Enum):
    """Budget spending categories."""
    GROCERIES = "groceries"
    DINING = "dining"
    TRANSPORTATION = "transportation"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"
    OTHER = "other"


class BillStatus(Enum):
    """Bill payment status."""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


@dataclass
class Transaction:
    """
    A record of money movement (sent or received) between accounts.
    
    Attributes:
        id: Unique identifier for the transaction
        description: Human-readable description of the transaction
        amount: Transaction amount (positive for incoming, negative for outgoing)
        date: Timestamp when the transaction occurred
        recipient: Name of the recipient (for outgoing transfers)
        category: Budget category for expense tracking
    """
    id: str
    description: str
    amount: float
    date: datetime
    recipient: Optional[str] = None
    category: Optional[BudgetCategory] = None


@dataclass
class Contact:
    """
    A predefined recipient that the user can send money to.
    
    Attributes:
        id: Unique identifier for the contact
        name: Display name of the contact
        avatar_color: Color for UI avatar display
    """
    id: str
    name: str
    avatar_color: str


@dataclass
class ActionHistoryEntry:
    """
    A log entry for voice-triggered financial operations.
    
    Attributes:
        id: Unique identifier for the action entry
        action: Name of the tool/action executed
        description: Human-readable description of what was done
        timestamp: When the action was performed
    """
    id: str
    action: str
    description: str
    timestamp: datetime


@dataclass
class Stock:
    """
    Stock quote information.
    
    Attributes:
        symbol: Stock ticker symbol
        name: Company name
        price: Current price
        change: Price change from previous close
        change_percent: Percentage change
        last_updated: When the quote was last updated
    """
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    last_updated: datetime


@dataclass
class Budget:
    """
    Monthly budget for a spending category.
    
    Attributes:
        id: Unique identifier
        category: Budget category
        limit: Monthly spending limit
        spent: Amount spent this month
        month: Budget month (YYYY-MM format)
    """
    id: str
    category: BudgetCategory
    limit: float
    spent: float
    month: str


@dataclass
class Bill:
    """
    A recurring bill or payment due.
    
    Attributes:
        id: Unique identifier
        name: Bill name/payee
        amount: Amount due
        due_date: Payment due date
        status: Payment status
        category: Associated budget category
    """
    id: str
    name: str
    amount: float
    due_date: date
    status: BillStatus
    category: BudgetCategory


@dataclass
class FinancialGoal:
    """
    A savings or financial goal.
    
    Attributes:
        id: Unique identifier
        name: Goal name
        target_amount: Target amount to save
        current_amount: Amount saved so far
        target_date: Target completion date
        description: Optional description
    """
    id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: Optional[date] = None
    description: Optional[str] = None


@dataclass
class PortfolioHolding:
    """
    A stock holding in the user's portfolio.
    
    Attributes:
        symbol: Stock ticker symbol
        shares: Number of shares owned
        average_cost: Average cost per share
        purchase_date: Date of first purchase
    """
    symbol: str
    shares: float
    average_cost: float
    purchase_date: date
