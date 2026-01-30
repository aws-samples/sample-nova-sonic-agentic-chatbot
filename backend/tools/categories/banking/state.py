"""
Banking state management singleton.
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a banking transaction."""
    id: str
    description: str
    amount: float
    date: datetime
    recipient: Optional[str] = None


@dataclass
class Contact:
    """Represents a contact for transfers."""
    id: str
    name: str
    avatar_color: str


@dataclass
class ActionHistoryEntry:
    """Represents an action in the history."""
    id: str
    action: str
    description: str
    timestamp: datetime


class BankingState:
    """
    Singleton class that manages all banking data in-memory.
    
    This ensures all tools access the same state instance.
    State resets when the application restarts.
    """
    _instance: Optional['BankingState'] = None
    
    def __new__(cls) -> 'BankingState':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the banking state with default values."""
        self.balance: float = 5000.00
        self.transactions: List[Transaction] = []
        self.contacts: List[Contact] = []
        self.action_history: List[ActionHistoryEntry] = []
        self._seed_mock_data()
    
    def _seed_mock_data(self) -> None:
        """Populate the state with realistic mock data for demo purposes."""
        now = datetime.now()
        
        # Initialize contacts
        self.contacts = [
            Contact(id=str(uuid.uuid4()), name="Alice", avatar_color="blue"),
            Contact(id=str(uuid.uuid4()), name="Bob", avatar_color="green"),
            Contact(id=str(uuid.uuid4()), name="Charlie", avatar_color="purple"),
        ]
        
        # Initialize transactions
        self.transactions = [
            Transaction(
                id=str(uuid.uuid4()),
                description="Direct Deposit",
                amount=2500.00,
                date=now - timedelta(days=5)
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Grocery Store",
                amount=-85.50,
                date=now - timedelta(days=3)
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Gas Station",
                amount=-45.00,
                date=now - timedelta(days=2)
            ),
            Transaction(
                id=str(uuid.uuid4()),
                description="Online Purchase",
                amount=-120.00,
                date=now - timedelta(days=1)
            ),
        ]

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Return the current state as a dictionary for UI consumption."""
        return {
            "balance": self.balance,
            "transactions": [
                {
                    "id": t.id,
                    "description": t.description,
                    "amount": t.amount,
                    "date": t.date.isoformat(),
                    "recipient": t.recipient
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
            ]
        }
    
    def add_transaction(
        self, description: str, amount: float, recipient: Optional[str] = None
    ) -> Transaction:
        """Add a new transaction and update the balance."""
        transaction = Transaction(
            id=str(uuid.uuid4()), description=description,
            amount=amount, date=datetime.now(), recipient=recipient
        )
        self.transactions.append(transaction)
        self.balance += amount
        return transaction
    
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
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance. Useful for testing."""
        if cls._instance is not None:
            cls._instance._initialize()
