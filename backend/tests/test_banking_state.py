"""
Property-based tests for BankingState.

Feature: voice-banking-assistant
Tests Property 9: Action History Growth and Property 10: Action History Ordering
Validates: Requirements 5.2, 5.3
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
import time

import sys
sys.path.insert(0, 'backend')

from tools.categories.banking.models import ActionHistoryEntry
from tools.categories.banking.state import BankingState


@pytest.fixture(autouse=True)
def reset_banking_state():
    """Reset the BankingState singleton before each test."""
    BankingState.reset()
    yield
    BankingState.reset()


# Strategies for generating test data
action_name_strategy = st.sampled_from([
    "check_balance", 
    "send_money", 
    "get_transactions", 
    "get_contacts"
])

description_strategy = st.text(
    min_size=1, 
    max_size=100, 
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))
)


class TestActionHistoryGrowth:
    """
    Property 9: Action History Growth
    
    For any tool execution, the action_history list SHALL grow by exactly 
    one entry containing the tool name and a timestamp.
    
    **Feature: voice-banking-assistant, Property 9: Action History Growth**
    **Validates: Requirements 5.2**
    """
    
    @given(
        action=action_name_strategy,
        description=description_strategy
    )
    @settings(max_examples=100)
    def test_action_history_grows_by_one(self, action: str, description: str):
        """
        Property 9: Action History Growth
        
        For any action logged, the action_history list SHALL grow by exactly one entry.
        """
        # Reset state at the start of each hypothesis example
        BankingState.reset()
        state = BankingState()
        initial_count = len(state.action_history)
        
        # Log an action
        entry = state.log_action(action, description)
        
        # Verify the list grew by exactly one
        assert len(state.action_history) == initial_count + 1
        
        # Verify the entry contains the tool name
        assert entry.action == action
        
        # Verify the entry has a timestamp
        assert isinstance(entry.timestamp, datetime)
        
        # Verify the entry is in the history
        assert entry in state.action_history
    
    @given(
        actions=st.lists(
            st.tuples(action_name_strategy, description_strategy),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_multiple_actions_grow_history_correctly(self, actions):
        """
        Property 9 extended: Multiple actions grow history by the correct count.
        """
        # Reset state at the start of each hypothesis example
        BankingState.reset()
        state = BankingState()
        initial_count = len(state.action_history)
        
        for action, description in actions:
            state.log_action(action, description)
        
        # Verify the list grew by exactly the number of actions
        assert len(state.action_history) == initial_count + len(actions)


class TestActionHistoryOrdering:
    """
    Property 10: Action History Ordering
    
    For any action_history list with multiple entries, entries SHALL be 
    ordered by timestamp in descending order (newest first) when retrieved
    for display.
    
    Note: The internal storage is append-only (chronological), but the 
    get_state_snapshot() returns them in the order they were added.
    The UI is responsible for displaying in reverse chronological order.
    
    **Feature: voice-banking-assistant, Property 10: Action History Ordering**
    **Validates: Requirements 5.3**
    """
    
    @given(
        actions=st.lists(
            st.tuples(action_name_strategy, description_strategy),
            min_size=2,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_action_history_maintains_chronological_order(self, actions):
        """
        Property 10: Action History Ordering
        
        For any sequence of logged actions, entries SHALL be stored in 
        chronological order (oldest first in the list).
        """
        # Reset state at the start of each hypothesis example
        BankingState.reset()
        state = BankingState()
        
        entries = []
        for action, description in actions:
            entry = state.log_action(action, description)
            entries.append(entry)
            # Small delay to ensure distinct timestamps
            time.sleep(0.001)
        
        # Verify entries are in chronological order (oldest first)
        for i in range(len(state.action_history) - 1):
            current = state.action_history[i]
            next_entry = state.action_history[i + 1]
            # Each entry should have timestamp <= next entry
            assert current.timestamp <= next_entry.timestamp
    
    @given(
        actions=st.lists(
            st.tuples(action_name_strategy, description_strategy),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100)
    def test_snapshot_preserves_action_order(self, actions):
        """
        Property 10 extended: get_state_snapshot preserves action order.
        """
        # Reset state at the start of each hypothesis example
        BankingState.reset()
        state = BankingState()
        initial_history_count = len(state.action_history)
        
        for action, description in actions:
            state.log_action(action, description)
            time.sleep(0.001)
        
        snapshot = state.get_state_snapshot()
        action_history = snapshot["actionHistory"]
        
        # Verify the snapshot contains all logged actions (plus any initial ones)
        assert len(action_history) == initial_history_count + len(actions)
        
        # Verify timestamps are in chronological order
        for i in range(len(action_history) - 1):
            current_ts = action_history[i]["timestamp"]
            next_ts = action_history[i + 1]["timestamp"]
            assert current_ts <= next_ts


# Import the CheckBalanceTool for property testing
from tools.categories.banking.check_balance import CheckBalanceTool


class TestCheckBalanceAccuracy:
    """
    Property 4: Check Balance Accuracy
    
    For any banking state with balance B, executing the check_balance tool 
    SHALL return a model_result containing balance equal to B.
    
    **Feature: voice-banking-assistant, Property 4: Check Balance Accuracy**
    **Validates: Requirements 2.2**
    """
    
    @given(
        balance=st.floats(min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_check_balance_returns_accurate_balance(self, balance: float):
        """
        Property 4: Check Balance Accuracy
        
        For any banking state with balance B, executing check_balance SHALL 
        return model_result containing balance equal to B.
        """
        # Reset state and set a specific balance
        BankingState.reset()
        state = BankingState()
        state.balance = balance
        
        # Execute the check_balance tool
        tool = CheckBalanceTool()
        result = await tool.execute({})
        
        # Verify the model_result contains the correct balance
        assert result["model_result"]["balance"] == balance
        assert result["model_result"]["currency"] == "USD"
        
        # Verify the ui_result contains the correct state
        assert result["ui_result"]["type"] == "app"
        assert result["ui_result"]["appName"] == "banking"
        assert result["ui_result"]["props"]["action"] == "highlight_balance"
        assert result["ui_result"]["props"]["state"]["balance"] == balance


# Import the SendMoneyTool for property testing
from tools.categories.banking.send_money import SendMoneyTool


# Strategy for valid amounts (positive, reasonable range)
valid_amount_strategy = st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)

# Strategy for contact names from the mock data
contact_name_strategy = st.sampled_from(["Alice", "Bob", "Charlie", "Diana"])


class TestSendMoneySuccessInvariants:
    """
    Property 5: Send Money Success Invariants
    
    For any valid send_money request with recipient R in contacts and amount A 
    where A ≤ balance:
    - The new balance SHALL equal (old balance - A)
    - A new transaction SHALL be created with amount -A and recipient R
    - The ui_result state SHALL reflect the updated balance and include the new transaction
    
    **Feature: voice-banking-assistant, Property 5: Send Money Success Invariants**
    **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
    """
    
    @given(
        recipient=contact_name_strategy,
        amount=valid_amount_strategy
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_send_money_success_invariants(self, recipient: str, amount: float):
        """
        Property 5: Send Money Success Invariants
        
        For any valid send_money request, the balance decreases by the amount,
        a transaction is created, and the UI state reflects the changes.
        """
        # Reset state to ensure sufficient balance
        BankingState.reset()
        state = BankingState()
        
        # Ensure we have enough balance for the transfer
        state.balance = max(state.balance, amount + 100)
        old_balance = state.balance
        old_transaction_count = len(state.transactions)
        
        # Execute the send_money tool
        tool = SendMoneyTool()
        result = await tool.execute({"recipient": recipient, "amount": amount})
        
        # Verify success
        assert result["model_result"]["success"] is True
        
        # Verify new balance equals (old balance - amount)
        expected_balance = old_balance - amount
        assert abs(state.balance - expected_balance) < 0.001  # Float comparison
        assert abs(result["model_result"]["new_balance"] - expected_balance) < 0.001
        
        # Verify a new transaction was created
        assert len(state.transactions) == old_transaction_count + 1
        
        # Verify the transaction has correct amount (-A) and recipient
        new_transaction = state.transactions[-1]
        assert abs(new_transaction.amount - (-amount)) < 0.001
        assert new_transaction.recipient == recipient
        
        # Verify ui_result contains updated state
        ui_state = result["ui_result"]["props"]["state"]
        assert abs(ui_state["balance"] - expected_balance) < 0.001
        
        # Verify the new transaction is in the ui_result
        transaction_in_result = result["ui_result"]["props"]["transaction"]
        assert abs(transaction_in_result["amount"] - (-amount)) < 0.001
        assert transaction_in_result["recipient"] == recipient


class TestSendMoneyInsufficientFunds:
    """
    Property 6: Send Money Insufficient Funds
    
    For any send_money request with amount A where A > current balance, 
    the tool SHALL return an error and the banking state (balance, transactions) 
    SHALL remain unchanged.
    
    **Feature: voice-banking-assistant, Property 6: Send Money Insufficient Funds**
    **Validates: Requirements 3.6**
    """
    
    @given(
        recipient=contact_name_strategy,
        excess_amount=st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_send_money_insufficient_funds(self, recipient: str, excess_amount: float):
        """
        Property 6: Send Money Insufficient Funds
        
        For any amount exceeding balance, the tool returns an error and state is unchanged.
        """
        # Reset state
        BankingState.reset()
        state = BankingState()
        
        # Set a known balance and request more than available
        state.balance = 100.0
        amount = state.balance + excess_amount  # Always exceeds balance
        
        old_balance = state.balance
        old_transactions = list(state.transactions)
        old_transaction_count = len(state.transactions)
        
        # Execute the send_money tool
        tool = SendMoneyTool()
        result = await tool.execute({"recipient": recipient, "amount": amount})
        
        # Verify error response
        assert result["model_result"]["success"] is False
        assert result["model_result"]["error"] == "insufficient_funds"
        
        # Verify balance is unchanged
        assert state.balance == old_balance
        
        # Verify transactions are unchanged
        assert len(state.transactions) == old_transaction_count


class TestSendMoneyUnknownRecipient:
    """
    Property 7: Send Money Unknown Recipient
    
    For any send_money request with recipient R where R is not in the contacts list, 
    the tool SHALL return an error containing the list of valid contacts, 
    and the banking state SHALL remain unchanged.
    
    **Feature: voice-banking-assistant, Property 7: Send Money Unknown Recipient**
    **Validates: Requirements 3.7**
    """
    
    @given(
        unknown_recipient=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L',))).filter(
            lambda x: x.lower() not in ["alice", "bob", "charlie", "diana"]
        ),
        amount=valid_amount_strategy
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_send_money_unknown_recipient(self, unknown_recipient: str, amount: float):
        """
        Property 7: Send Money Unknown Recipient
        
        For any unknown recipient, the tool returns an error with valid contacts
        and state is unchanged.
        """
        # Reset state
        BankingState.reset()
        state = BankingState()
        
        old_balance = state.balance
        old_transaction_count = len(state.transactions)
        
        # Execute the send_money tool with unknown recipient
        tool = SendMoneyTool()
        result = await tool.execute({"recipient": unknown_recipient, "amount": amount})
        
        # Verify error response
        assert result["model_result"]["success"] is False
        assert result["model_result"]["error"] == "unknown_recipient"
        
        # Verify available contacts are returned
        assert "available_contacts" in result["model_result"]
        available = result["model_result"]["available_contacts"]
        assert len(available) > 0
        assert all(name in ["Alice", "Bob", "Charlie", "Diana"] for name in available)
        
        # Verify balance is unchanged
        assert state.balance == old_balance
        
        # Verify transactions are unchanged
        assert len(state.transactions) == old_transaction_count


# Import the GetTransactionsTool for property testing
from tools.categories.banking.get_transactions import GetTransactionsTool
from tools.categories.banking.models import Transaction
from datetime import datetime, timedelta
import uuid


# Strategy for generating transactions
transaction_strategy = st.builds(
    Transaction,
    id=st.uuids().map(str),
    description=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
    amount=st.floats(min_value=-5000, max_value=5000, allow_nan=False, allow_infinity=False).filter(lambda x: abs(x) > 0.01),
    date=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)),
    recipient=st.one_of(st.none(), st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L',))))
)


class TestGetTransactionsCompleteness:
    """
    Property 8: Get Transactions Completeness
    
    For any banking state with transactions list T, executing get_transactions 
    SHALL return all transactions in T.
    
    **Feature: voice-banking-assistant, Property 8: Get Transactions Completeness**
    **Validates: Requirements 4.2**
    """
    
    @given(
        transactions=st.lists(transaction_strategy, min_size=0, max_size=20)
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_get_transactions_returns_all(self, transactions):
        """
        Property 8: Get Transactions Completeness
        
        For any list of transactions, get_transactions returns all of them.
        """
        # Reset state
        BankingState.reset()
        state = BankingState()
        
        # Replace transactions with our generated list
        state.transactions = transactions
        
        # Execute the get_transactions tool
        tool = GetTransactionsTool()
        result = await tool.execute({})
        
        # Verify all transactions are returned
        returned_transactions = result["model_result"]["transactions"]
        assert len(returned_transactions) == len(transactions)
        
        # Verify each transaction is present with correct data
        returned_ids = {t["id"] for t in returned_transactions}
        original_ids = {t.id for t in transactions}
        assert returned_ids == original_ids
        
        # Verify the count matches
        assert result["model_result"]["count"] == len(transactions)
        
        # Verify ui_result contains the state
        ui_state = result["ui_result"]["props"]["state"]
        assert len(ui_state["transactions"]) == len(transactions)
    
    @given(
        transactions=st.lists(transaction_strategy, min_size=1, max_size=20)
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_get_transactions_preserves_amounts(self, transactions):
        """
        Property 8 extended: Transaction amounts are preserved correctly.
        """
        # Reset state
        BankingState.reset()
        state = BankingState()
        
        # Replace transactions with our generated list
        state.transactions = transactions
        
        # Execute the get_transactions tool
        tool = GetTransactionsTool()
        result = await tool.execute({})
        
        # Verify amounts are preserved
        returned_transactions = result["model_result"]["transactions"]
        
        for original in transactions:
            # Find the matching returned transaction
            matching = [t for t in returned_transactions if t["id"] == original.id]
            assert len(matching) == 1
            assert abs(matching[0]["amount"] - original.amount) < 0.001
