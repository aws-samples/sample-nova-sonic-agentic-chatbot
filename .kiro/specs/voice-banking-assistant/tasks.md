# Implementation Plan: Voice Banking Assistant

## Overview

This implementation transforms the existing Nova Sonic voice agent demo into a voice-powered banking assistant. We'll build the backend banking tools first, then create the frontend banking dashboard, and finally wire everything together. The approach ensures each step builds on the previous one with no orphaned code.

## Tasks

- [x] 1. Create banking state management and data models
  - [x] 1.1 Create the banking module directory structure and data models
    - Create `backend/tools/categories/banking/` directory
    - Create `models.py` with Transaction, Contact, ActionHistoryEntry dataclasses
    - Create `__init__.py` to export models
    - _Requirements: 7.1, 7.2, 7.3_
  - [x] 1.2 Implement BankingState singleton with mock data initialization
    - Create `state.py` with BankingState class
    - Implement `_seed_mock_data()` with $5000 balance, 8 transactions, 4 contacts
    - Implement `get_state_snapshot()` method
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  - [x] 1.3 Write property tests for BankingState initialization
    - **Property 9: Action History Growth** - verify action logging
    - **Property 10: Action History Ordering** - verify chronological order
    - **Validates: Requirements 5.2, 5.3**

- [x] 2. Implement backend banking tools
  - [x] 2.1 Implement CheckBalanceTool
    - Create `check_balance.py` extending BaseTool
    - Return current balance in model_result
    - Return app ui_result with highlight_balance action
    - Log action to history
    - _Requirements: 2.1, 2.2, 2.3_
  - [x] 2.2 Write property test for CheckBalanceTool
    - **Property 4: Check Balance Accuracy**
    - **Validates: Requirements 2.2**
  - [x] 2.3 Implement SendMoneyTool
    - Create `send_money.py` extending BaseTool
    - Validate recipient exists in contacts
    - Validate amount <= balance and amount > 0
    - Deduct amount, create transaction, log action
    - Return success with updated state or error
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  - [x] 2.4 Write property tests for SendMoneyTool
    - **Property 5: Send Money Success Invariants**
    - **Property 6: Send Money Insufficient Funds**
    - **Property 7: Send Money Unknown Recipient**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
  - [x] 2.5 Implement GetTransactionsTool
    - Create `get_transactions.py` extending BaseTool
    - Return all transactions in model_result
    - Return app ui_result with show_transactions action
    - Log action to history
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 2.6 Write property test for GetTransactionsTool
    - **Property 8: Get Transactions Completeness**
    - **Validates: Requirements 4.2**
  - [x] 2.7 Register banking tools in ToolManager
    - Update `backend/tools/tool_manager.py` to import and register banking tools
    - Update `backend/tools/categories/banking/__init__.py` exports
    - _Requirements: 2.1, 3.1, 4.1_

- [x] 3. Checkpoint - Backend tools complete
  - Ensure all backend tests pass
  - Verify tools are registered and accessible
  - Ask the user if questions arise

- [x] 4. Create frontend banking components
  - [x] 4.1 Create BankingApp main component structure
    - Create `frontend/components/apps/BankingApp.tsx`
    - Define TypeScript interfaces for BankingState, Transaction, Contact, ActionHistoryEntry
    - Create component shell with props interface
    - _Requirements: 1.1, 1.2, 1.3, 6.1_
  - [x] 4.2 Implement BalanceCard component
    - Create balance display with large font, currency formatting
    - Add highlight animation when action is 'highlight_balance'
    - Use Revolut-style dark card design
    - _Requirements: 1.1, 1.4, 2.3_
  - [x] 4.3 Implement TransactionList component
    - Create scrollable transaction list
    - Format amounts with +/- prefix and green/red colors
    - Show date, description, amount for each transaction
    - Add animation for new transactions
    - _Requirements: 1.2, 1.5, 1.6, 3.5_
  - [x] 4.4 Write property tests for transaction formatting
    - **Property 1: Transaction Amount Formatting**
    - **Property 2: Transaction List Completeness**
    - **Validates: Requirements 1.2, 1.5, 1.6**
  - [x] 4.5 Implement ContactsList component
    - Create horizontal scrollable contact avatars
    - Show contact name and colored avatar
    - _Requirements: 1.3_
  - [x] 4.6 Write property test for contacts rendering
    - **Property 3: Contacts List Completeness**
    - **Validates: Requirements 1.3**
  - [x] 4.7 Implement ActionHistory component
    - Create collapsible action history panel
    - Show action name, description, timestamp
    - Display in reverse chronological order
    - Add slide-in animation for new entries
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 5. Integrate BankingApp with tool output system
  - [x] 5.1 Update ToolOutput component to render BankingApp
    - Modify `frontend/components/tool-outputs/ToolOutput.tsx`
    - Add case for `appName === 'banking'` to render BankingApp
    - Pass props from tool output to BankingApp
    - _Requirements: 2.3, 3.4, 3.5, 4.3_
  - [x] 5.2 Update types.ts with BankingAppToolOutput interface
    - Add BankingAppToolOutput to types
    - Export updated ToolOutput union type
    - _Requirements: 2.3, 3.4, 4.3_

- [x] 6. Update page layout for banking dashboard
  - [x] 6.1 Restructure page.tsx layout
    - Replace generic tool output area with BankingApp as default view
    - Maintain voice chat panel on right side
    - Add state management for banking data
    - _Requirements: 6.1, 6.2, 6.4_
  - [x] 6.2 Add REST endpoint for initial state fetch
    - Create `backend/api/apps/banking.py` with GET /api/banking/state endpoint
    - Return initial BankingState snapshot
    - _Requirements: 7.1, 7.2, 7.3_
  - [x] 6.3 Implement frontend state initialization
    - Fetch initial state on component mount
    - Update state when tool outputs are received
    - _Requirements: 1.1, 1.2, 1.3, 6.1_

- [x] 7. Final integration and polish
  - [x] 7.1 Add visual feedback for voice agent activity
    - Show speaking indicator when agent is responding
    - Pulse animation on balance during check_balance
    - _Requirements: 6.3, 2.3_
  - [x] 7.2 Style refinements for Revolut aesthetic
    - Apply dark theme option
    - Refine card shadows and borders
    - Ensure smooth animations
    - _Requirements: 1.4_

- [x] 8. Final checkpoint - All features complete
  - Ensure all tests pass
  - Verify voice commands work end-to-end
  - Test: check balance, send money, view transactions
  - Ask the user if questions arise

## Notes

- All tasks including property tests are required
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The BankingState singleton ensures all tools share the same state
- State resets on page refresh (no persistence needed for demo)
