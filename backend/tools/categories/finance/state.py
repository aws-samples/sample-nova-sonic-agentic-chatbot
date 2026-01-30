"""
Finance state management singleton for the Financial Assistant.
"""
import uuid
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any

from .models import (
    Transaction, Contact, ActionHistoryEntry, Stock, Budget, Bill, FinancialGoal,
    BudgetCategory, BillStatus, PortfolioHolding
)


class FinanceState:
    """
    Singleton class that manages all financial data in-memory.
    
    This ensures all tools access the same state instance.
    State resets when the application restarts.
    """
    _instance: Optional['FinanceState'] = None
    
    def __new__(cls) -> 'FinanceState':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the finance state with default values."""
        self.balance: float = 12500.00
        self.savings_balance: float = 8500.00
        self.transactions: List[Transaction] = []
        self.contacts: List[Contact] = []
        self.action_history: List[ActionHistoryEntry] = []
        self.stocks: Dict[str, Stock] = {}
        self.budgets: List[Budget] = []
        self.bills: List[Bill] = []
        self.goals: List[FinancialGoal] = []
        self.portfolio: List[PortfolioHolding] = []
        self._seed_mock_data()
    
    def _seed_mock_data(self) -> None:
        """Populate the state with realistic mock data for demo purposes."""
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        
        # Initialize contacts
        self.contacts = [
            Contact(id=str(uuid.uuid4()), name="Alice", avatar_color="blue"),
            Contact(id=str(uuid.uuid4()), name="Bob", avatar_color="green"),
            Contact(id=str(uuid.uuid4()), name="Charlie", avatar_color="purple"),
            Contact(id=str(uuid.uuid4()), name="Diana", avatar_color="orange"),
        ]
        
        # Initialize transactions with categories
        self.transactions = [
            Transaction(
                id=str(uuid.uuid4()),
                description="Salary Deposit",
                amount=5500.00,
                date=now - timedelta(days=7),
                category=None
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Whole Foods Market",
                amount=-125.50,
                date=now - timedelta(days=6),
                category=BudgetCategory.GROCERIES
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Uber Ride",
                amount=-24.80,
                date=now - timedelta(days=5),
                category=BudgetCategory.TRANSPORTATION
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Netflix Subscription",
                amount=-15.99,
                date=now - timedelta(days=4),
                category=BudgetCategory.ENTERTAINMENT
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Electric Bill Payment",
                amount=-145.00,
                date=now - timedelta(days=3),
                recipient="Power Company",
                category=BudgetCategory.UTILITIES
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Restaurant - Italian Place",
                amount=-68.50,
                date=now - timedelta(days=2),
                category=BudgetCategory.DINING
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Dividend Payment - AAPL",
                amount=45.00,
                date=now - timedelta(days=1),
                category=None
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Amazon Purchase",
                amount=-89.99,
                date=now - timedelta(hours=12),
                category=BudgetCategory.SHOPPING
            ),
        ]
        
        # Initialize stock watchlist with mock data
        self.stocks = {
            "AAPL": Stock(
                symbol="AAPL", name="Apple Inc.", price=178.50,
                change=2.35, change_percent=1.33, last_updated=now
            ),
            "GOOGL": Stock(
                symbol="GOOGL", name="Alphabet Inc.", price=141.25,
                change=-0.85, change_percent=-0.60, last_updated=now
            ),
            "MSFT": Stock(
                symbol="MSFT", name="Microsoft Corporation", price=378.90,
                change=4.20, change_percent=1.12, last_updated=now
            ),
            "AMZN": Stock(
                symbol="AMZN", name="Amazon.com Inc.", price=185.60,
                change=1.45, change_percent=0.79, last_updated=now
            ),
            "TSLA": Stock(
                symbol="TSLA", name="Tesla Inc.", price=248.75,
                change=-5.30, change_percent=-2.09, last_updated=now
            ),
        }
        
        # Initialize monthly budgets
        self.budgets = [
            Budget(id=str(uuid.uuid4()), category=BudgetCategory.GROCERIES, 
                   limit=600.00, spent=125.50, month=current_month),
            Budget(id=str(uuid.uuid4()), category=BudgetCategory.DINING, 
                   limit=300.00, spent=68.50, month=current_month),
            Budget(id=str(uuid.uuid4()), category=BudgetCategory.TRANSPORTATION, 
                   limit=200.00, spent=24.80, month=current_month),
            Budget(id=str(uuid.uuid4()), category=BudgetCategory.UTILITIES, 
                   limit=250.00, spent=145.00, month=current_month),
            Budget(id=str(uuid.uuid4()), category=BudgetCategory.ENTERTAINMENT, 
                   limit=150.00, spent=15.99, month=current_month),
            Budget(id=str(uuid.uuid4()), category=BudgetCategory.SHOPPING, 
                   limit=400.00, spent=89.99, month=current_month),
        ]
        
        # Initialize bills
        today = date.today()
        self.bills = [
            Bill(id=str(uuid.uuid4()), name="Rent", amount=1800.00,
                 due_date=today + timedelta(days=5), status=BillStatus.PENDING,
                 category=BudgetCategory.OTHER),
            Bill(id=str(uuid.uuid4()), name="Internet - Comcast", amount=79.99,
                 due_date=today + timedelta(days=10), status=BillStatus.PENDING,
                 category=BudgetCategory.UTILITIES),
            Bill(id=str(uuid.uuid4()), name="Car Insurance", amount=125.00,
                 due_date=today + timedelta(days=15), status=BillStatus.PENDING,
                 category=BudgetCategory.TRANSPORTATION),
            Bill(id=str(uuid.uuid4()), name="Phone Bill", amount=85.00,
                 due_date=today - timedelta(days=2), status=BillStatus.OVERDUE,
                 category=BudgetCategory.UTILITIES),
        ]
        
        # Initialize financial goals
        self.goals = [
            FinancialGoal(
                id=str(uuid.uuid4()), name="Emergency Fund",
                target_amount=15000.00, current_amount=8500.00,
                target_date=date(2026, 12, 31),
                description="6 months of expenses"
            ),
            FinancialGoal(
                id=str(uuid.uuid4()), name="Vacation Fund",
                target_amount=5000.00, current_amount=1200.00,
                target_date=date(2026, 6, 1),
                description="Summer trip to Europe"
            ),
            FinancialGoal(
                id=str(uuid.uuid4()), name="New Car Down Payment",
                target_amount=10000.00, current_amount=3500.00,
                target_date=date(2027, 1, 1),
                description="Down payment for new vehicle"
            ),
        ]
        
        # Initialize portfolio with some existing holdings
        self.portfolio = [
            PortfolioHolding(
                symbol="AAPL", shares=10, average_cost=165.00,
                purchase_date=date.today() - timedelta(days=90)
            ),
            PortfolioHolding(
                symbol="MSFT", shares=5, average_cost=350.00,
                purchase_date=date.today() - timedelta(days=60)
            ),
        ]

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Return the current state as a dictionary for UI consumption."""
        return {
            "balance": self.balance,
            "savingsBalance": self.savings_balance,
            "transactions": [
                {
                    "id": t.id,
                    "description": t.description,
                    "amount": t.amount,
                    "date": t.date.isoformat(),
                    "recipient": t.recipient,
                    "category": t.category.value if t.category else None
                }
                for t in self.transactions
            ],
            "contacts": [
                {"id": c.id, "name": c.name, "avatarColor": c.avatar_color}
                for c in self.contacts
            ],
            "actionHistory": [
                {
                    "id": a.id, "action": a.action,
                    "description": a.description, "timestamp": a.timestamp.isoformat()
                }
                for a in self.action_history
            ],
            "budgets": [
                {
                    "id": b.id, "category": b.category.value,
                    "limit": b.limit, "spent": b.spent, "month": b.month
                }
                for b in self.budgets
            ],
            "bills": [
                {
                    "id": b.id, "name": b.name, "amount": b.amount,
                    "dueDate": b.due_date.isoformat(), "status": b.status.value,
                    "category": b.category.value
                }
                for b in self.bills
            ],
            "goals": [
                {
                    "id": g.id, "name": g.name,
                    "targetAmount": g.target_amount, "currentAmount": g.current_amount,
                    "targetDate": g.target_date.isoformat() if g.target_date else None,
                    "description": g.description
                }
                for g in self.goals
            ],
            "portfolio": [
                {
                    "symbol": p.symbol, "shares": p.shares,
                    "averageCost": p.average_cost,
                    "purchaseDate": p.purchase_date.isoformat()
                }
                for p in self.portfolio
            ]
        }
    
    def add_transaction(
        self, description: str, amount: float, 
        recipient: Optional[str] = None, category: Optional[BudgetCategory] = None
    ) -> Transaction:
        """Add a new transaction and update the balance."""
        transaction = Transaction(
            id=str(uuid.uuid4()), description=description,
            amount=amount, date=datetime.now(),
            recipient=recipient, category=category
        )
        self.transactions.append(transaction)
        self.balance += amount
        
        # Update budget if category is specified and amount is negative (expense)
        if category and amount < 0:
            self._update_budget_spent(category, abs(amount))
        
        return transaction
    
    def _update_budget_spent(self, category: BudgetCategory, amount: float) -> None:
        """Update the spent amount for a budget category."""
        current_month = datetime.now().strftime("%Y-%m")
        for budget in self.budgets:
            if budget.category == category and budget.month == current_month:
                budget.spent += amount
                break
    
    def log_action(self, action: str, description: str) -> ActionHistoryEntry:
        """Log a voice-triggered action to the history."""
        entry = ActionHistoryEntry(
            id=str(uuid.uuid4()), action=action,
            description=description, timestamp=datetime.now()
        )
        self.action_history.append(entry)
        return entry
    
    def find_contact_by_name(self, name: str) -> Optional[Contact]:
        """Find a contact by name (case-insensitive)."""
        name_lower = name.lower()
        for contact in self.contacts:
            if contact.name.lower() == name_lower:
                return contact
        return None
    
    def get_contact_names(self) -> List[str]:
        """Get a list of all contact names."""
        return [c.name for c in self.contacts]
    
    def get_stock(self, symbol: str) -> Optional[Stock]:
        """Get stock quote by symbol."""
        return self.stocks.get(symbol.upper())
    
    def get_bill_by_name(self, name: str) -> Optional[Bill]:
        """Find a bill by name (case-insensitive partial match)."""
        name_lower = name.lower()
        for bill in self.bills:
            if name_lower in bill.name.lower():
                return bill
        return None
    
    def pay_bill(self, bill: Bill) -> Transaction:
        """Pay a bill and create a transaction."""
        bill.status = BillStatus.PAID
        return self.add_transaction(
            description=f"Bill Payment - {bill.name}",
            amount=-bill.amount,
            recipient=bill.name,
            category=bill.category
        )
    
    def add_to_portfolio(self, symbol: str, shares: float, price: float) -> PortfolioHolding:
        """Add shares to portfolio, updating existing holding or creating new one."""
        symbol = symbol.upper()
        
        # Check if we already have this stock
        for holding in self.portfolio:
            if holding.symbol == symbol:
                # Update average cost
                total_shares = holding.shares + shares
                total_cost = (holding.shares * holding.average_cost) + (shares * price)
                holding.average_cost = total_cost / total_shares
                holding.shares = total_shares
                return holding
        
        # Create new holding
        new_holding = PortfolioHolding(
            symbol=symbol,
            shares=shares,
            average_cost=price,
            purchase_date=date.today()
        )
        self.portfolio.append(new_holding)
        return new_holding
    
    def get_portfolio_holding(self, symbol: str) -> Optional[PortfolioHolding]:
        """Get a portfolio holding by symbol."""
        symbol = symbol.upper()
        for holding in self.portfolio:
            if holding.symbol == symbol:
                return holding
        return None
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance. Useful for testing."""
        if cls._instance is not None:
            cls._instance._initialize()
