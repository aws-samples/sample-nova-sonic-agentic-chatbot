# Design Document: Voice Banking Assistant

## Overview

This design transforms the existing Nova Sonic voice agent demo into a voice-powered banking assistant. The architecture leverages the existing tool system where backend Python tools handle business logic and return both model results (for the AI to speak) and UI results (for visual updates). The frontend will be restructured to show a banking dashboard on the left panel while maintaining the voice chat on the right.

The key insight is that we'll use the existing `type: 'app'` tool output pattern to render a custom `BankingApp` component that maintains its own state and receives updates via props from tool executions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                          │
├─────────────────────────────────┬───────────────────────────────────┤
│      Banking Dashboard          │         Voice Chat Panel          │
│  ┌───────────────────────────┐  │  ┌─────────────────────────────┐  │
│  │   Account Balance Card    │  │  │    Model/Language Select    │  │
│  │   $5,000.00              │  │  │    Connect/Disconnect       │  │
│  └───────────────────────────┘  │  │    Record/Stop              │  │
│  ┌───────────────────────────┐  │  ├─────────────────────────────┤  │
│  │   Quick Actions           │  │  │                             │  │
│  │   [Contacts List]         │  │  │    Chat Messages            │  │
│  └───────────────────────────┘  │  │    (User & Assistant)       │  │
│  ┌───────────────────────────┐  │  │                             │  │
│  │   Recent Transactions     │  │  └─────────────────────────────┘  │
│  │   - Coffee Shop  -$4.50   │  │                                   │
│  │   - Salary     +$3,000    │  │                                   │
│  └───────────────────────────┘  │                                   │
│  ┌───────────────────────────┐  │                                   │
│  │   Action History          │  │                                   │
│  │   [Voice command log]     │  │                                   │
│  └───────────────────────────┘  │                                   │
└─────────────────────────────────┴───────────────────────────────────┘
                                  │
                                  │ WebSocket
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                           │
├─────────────────────────────────────────────────────────────────────┤
│  ToolManager                                                        │
│  ├── CheckBalanceTool                                               │
│  ├── SendMoneyTool                                                  │
│  ├── GetTransactionsTool                                            │
│  └── GetContactsTool                                                │
├─────────────────────────────────────────────────────────────────────┤
│  BankingState (In-Memory)                                           │
│  ├── balance: float                                                 │
│  ├── transactions: List[Transaction]                                │
│  ├── contacts: List[Contact]                                        │
│  └── action_history: List[Action]                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Backend Components

#### 1. BankingState (Singleton)

A shared in-memory state manager that holds all banking data. This is a singleton so all tools access the same state.

```python
# backend/tools/categories/banking/state.py

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid

@dataclass
class Transaction:
    id: str
    description: str
    amount: float  # Positive for incoming, negative for outgoing
    date: datetime
    recipient: Optional[str] = None

@dataclass
class Contact:
    id: str
    name: str
    avatar_color: str  # For UI display

@dataclass
class ActionHistoryEntry:
    id: str
    action: str
    description: str
    timestamp: datetime

class BankingState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.balance: float = 5000.00
        self.transactions: List[Transaction] = []
        self.contacts: List[Contact] = []
        self.action_history: List[ActionHistoryEntry] = []
        self._seed_mock_data()
    
    def _seed_mock_data(self):
        # Initialize with mock data
        pass
    
    def get_state_snapshot(self) -> dict:
        # Return current state for UI
        pass
    
    def add_transaction(self, description: str, amount: float, recipient: str = None) -> Transaction:
        # Add new transaction and update balance
        pass
    
    def log_action(self, action: str, description: str) -> ActionHistoryEntry:
        # Log voice action to history
        pass
```

#### 2. Banking Tools

Each tool follows the existing `BaseTool` pattern, returning `model_result` for the AI and `ui_result` for the frontend.

```python
# Tool: check_balance
class CheckBalanceTool(BaseTool):
    config = {
        "name": "check_balance",
        "description": "Check the user's current account balance",
        "schema": {"type": "object", "properties": {}, "required": []}
    }
    
    async def execute(self, content: dict) -> dict:
        state = BankingState()
        state.log_action("check_balance", "Checked account balance")
        
        return self.format_response(
            model_result={"balance": state.balance, "currency": "USD"},
            ui_result={
                "type": "app",
                "appName": "banking",
                "props": {
                    "action": "highlight_balance",
                    "state": state.get_state_snapshot()
                }
            }
        )
```

```python
# Tool: send_money
class SendMoneyTool(BaseTool):
    config = {
        "name": "send_money",
        "description": "Send money to a contact. Requires recipient name and amount.",
        "schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Name of the recipient"},
                "amount": {"type": "number", "description": "Amount to send in USD"}
            },
            "required": ["recipient", "amount"]
        }
    }
    
    async def execute(self, content: dict) -> dict:
        state = BankingState()
        recipient = content.get("recipient")
        amount = content.get("amount")
        
        # Validation logic
        # Create transaction
        # Update balance
        # Log action
        
        return self.format_response(
            model_result={"success": True, "new_balance": state.balance, ...},
            ui_result={
                "type": "app",
                "appName": "banking",
                "props": {
                    "action": "money_sent",
                    "transaction": {...},
                    "state": state.get_state_snapshot()
                }
            }
        )
```

### Frontend Components

#### 1. BankingApp Component

The main banking dashboard component that receives state updates via props.

```typescript
// frontend/components/apps/BankingApp.tsx

interface BankingAppProps {
  action?: 'highlight_balance' | 'money_sent' | 'show_transactions';
  state?: BankingState;
  transaction?: Transaction;
}

interface BankingState {
  balance: number;
  transactions: Transaction[];
  contacts: Contact[];
  actionHistory: ActionHistoryEntry[];
}
```

#### 2. Sub-components

- `BalanceCard`: Displays current balance with highlight animation
- `TransactionList`: Shows recent transactions with add animation
- `ContactsList`: Shows available transfer recipients
- `ActionHistory`: Shows log of voice-triggered actions

### Frontend State Management

The banking state will be managed in two ways:
1. **Initial state**: Fetched via REST API on component mount
2. **Updates**: Received via WebSocket tool outputs that include the full state snapshot

This ensures the UI always reflects the backend state after each voice command.

## Data Models

### Transaction
```typescript
interface Transaction {
  id: string;
  description: string;
  amount: number;      // Positive = incoming, negative = outgoing
  date: string;        // ISO date string
  recipient?: string;  // For outgoing transfers
}
```

### Contact
```typescript
interface Contact {
  id: string;
  name: string;
  avatarColor: string; // Tailwind color class
}
```

### ActionHistoryEntry
```typescript
interface ActionHistoryEntry {
  id: string;
  action: string;      // Tool name
  description: string; // Human-readable description
  timestamp: string;   // ISO date string
}
```

### BankingState
```typescript
interface BankingState {
  balance: number;
  transactions: Transaction[];
  contacts: Contact[];
  actionHistory: ActionHistoryEntry[];
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Transaction Amount Formatting

*For any* transaction with a positive amount, the formatted display string SHALL contain a "+" prefix and green color indicator. *For any* transaction with a negative amount, the formatted display string SHALL contain a "-" prefix and red color indicator.

**Validates: Requirements 1.5, 1.6**

### Property 2: Transaction List Completeness

*For any* list of transactions provided to the Banking_UI, the rendered output SHALL contain the date, description, and amount for each transaction in the list.

**Validates: Requirements 1.2**

### Property 3: Contacts List Completeness

*For any* list of contacts provided to the Banking_UI, the rendered output SHALL display all contact names.

**Validates: Requirements 1.3**

### Property 4: Check Balance Accuracy

*For any* banking state with balance B, executing the check_balance tool SHALL return a model_result containing balance equal to B.

**Validates: Requirements 2.2**

### Property 5: Send Money Success Invariants

*For any* valid send_money request with recipient R in contacts and amount A where A ≤ balance:
- The new balance SHALL equal (old balance - A)
- A new transaction SHALL be created with amount -A and recipient R
- The ui_result state SHALL reflect the updated balance and include the new transaction

**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

### Property 6: Send Money Insufficient Funds

*For any* send_money request with amount A where A > current balance, the tool SHALL return an error and the banking state (balance, transactions) SHALL remain unchanged.

**Validates: Requirements 3.6**

### Property 7: Send Money Unknown Recipient

*For any* send_money request with recipient R where R is not in the contacts list, the tool SHALL return an error containing the list of valid contacts, and the banking state SHALL remain unchanged.

**Validates: Requirements 3.7**

### Property 8: Get Transactions Completeness

*For any* banking state with transactions list T, executing get_transactions SHALL return all transactions in T.

**Validates: Requirements 4.2**

### Property 9: Action History Growth

*For any* tool execution, the action_history list SHALL grow by exactly one entry containing the tool name and a timestamp.

**Validates: Requirements 5.2**

### Property 10: Action History Ordering

*For any* action_history list with multiple entries, entries SHALL be ordered by timestamp in descending order (newest first).

**Validates: Requirements 5.3**

## Error Handling

### Backend Error Handling

1. **Insufficient Funds**: When `send_money` is called with amount > balance:
   - Return `model_result` with `success: false` and `error: "insufficient_funds"`
   - Include current balance and requested amount in error details
   - Do not modify state

2. **Unknown Recipient**: When `send_money` is called with unknown recipient:
   - Return `model_result` with `success: false` and `error: "unknown_recipient"`
   - Include list of valid contact names
   - Do not modify state

3. **Invalid Amount**: When `send_money` is called with amount ≤ 0:
   - Return `model_result` with `success: false` and `error: "invalid_amount"`
   - Do not modify state

### Frontend Error Handling

1. **WebSocket Disconnection**: Show reconnection UI, disable voice controls
2. **Tool Execution Failure**: Display error message in action history
3. **State Sync Failure**: Fall back to last known good state

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples and edge cases:

1. **Initial State Tests**:
   - Verify mock data initialization (balance = $5000, 5-10 transactions, 3-5 contacts)
   - Verify transactions include both positive and negative amounts

2. **UI Rendering Tests**:
   - Verify balance card renders with correct formatting
   - Verify transaction list renders all items
   - Verify action history panel displays entries

3. **Edge Case Tests**:
   - Send exactly the full balance (should succeed)
   - Send $0 (should fail)
   - Send to recipient with case-insensitive matching

### Property-Based Tests

Property-based tests will use **Hypothesis** (Python) for backend and **fast-check** (TypeScript) for frontend, with minimum 100 iterations per property.

Each property test will be tagged with: **Feature: voice-banking-assistant, Property {number}: {property_text}**

1. **Backend Property Tests** (Hypothesis):
   - Property 4: Check balance accuracy
   - Property 5: Send money success invariants
   - Property 6: Insufficient funds handling
   - Property 7: Unknown recipient handling
   - Property 8: Get transactions completeness
   - Property 9: Action history growth
   - Property 10: Action history ordering

2. **Frontend Property Tests** (fast-check):
   - Property 1: Transaction amount formatting
   - Property 2: Transaction list completeness
   - Property 3: Contacts list completeness

### Test Data Generators

```python
# Backend generators (Hypothesis)
from hypothesis import strategies as st

valid_amount = st.floats(min_value=0.01, max_value=10000, allow_nan=False)
contact_name = st.sampled_from(["Alice", "Bob", "Charlie", "Diana", "Eve"])
transaction = st.builds(
    Transaction,
    id=st.uuids().map(str),
    description=st.text(min_size=1, max_size=50),
    amount=st.floats(min_value=-5000, max_value=5000, allow_nan=False),
    date=st.datetimes()
)
```

```typescript
// Frontend generators (fast-check)
import * as fc from 'fast-check';

const transactionArb = fc.record({
  id: fc.uuid(),
  description: fc.string({ minLength: 1, maxLength: 50 }),
  amount: fc.double({ min: -5000, max: 5000, noNaN: true }),
  date: fc.date().map(d => d.toISOString())
});
```

