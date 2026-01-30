export interface BaseToolOutput {
  type: string;
  content: {
    title?: string;
    description?: string;
    [key: string]: any;
  };
}

export interface TextToolOutput extends BaseToolOutput {
  type: 'text';
  content: {
    title?: string;
    [key: string]: any;
  };
}

export interface CardToolOutput extends BaseToolOutput {
  type: 'card';
  content: {
    title?: string;
    description?: string;
    details?: Record<string, string> | string;
    image?: string;
    imageAlt?: string;
    footer?: string | {
      text: string;
      action?: {
        text: string;
        url: string;
      };
    };
  };
}

export interface ImageToolOutput extends BaseToolOutput {
  type: 'image';
  content: {
    title?: string;
    description?: string;
    url: string;
    alt?: string;
  };
}

export interface VideoToolOutput extends BaseToolOutput {
  type: 'video';
  content: {
    title?: string;
    description?: string;
    url: string;
  };
}

export interface PdfToolOutput extends BaseToolOutput {
  type: 'pdf';
  content: {
    title?: string;
    description?: string;
    url: string;
  };
}

export interface ButtonToolOutput {
  type: 'button';
  content: {
    title: string;
    buttonText: string;
    id: string;
  };
}

export interface BargeinToolOutput extends BaseToolOutput {
  type: 'barge_in';
  content: {
    title?: string;
    description?: string;
    status: string;
    [key: string]: any;
  };
}

export interface AppToolOutput {
  type: 'app';
  appName: string;
  props?: Record<string, any>;
}

// Finance-specific types
export interface FinanceTransaction {
  id: string;
  description: string;
  amount: number;
  date: string;
  recipient?: string;
  category?: string;
}

export interface FinanceContact {
  id: string;
  name: string;
  avatarColor: string;
}

export interface FinanceActionHistoryEntry {
  id: string;
  action: string;
  description: string;
  timestamp: string;
}

export interface FinanceBudget {
  id: string;
  category: string;
  limit: number;
  spent: number;
  month: string;
}

export interface FinanceBill {
  id: string;
  name: string;
  amount: number;
  dueDate: string;
  status: string;
  category: string;
}

export interface FinancialGoal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  targetDate?: string;
  description?: string;
}

export interface FinanceState {
  balance: number;
  savingsBalance?: number;
  transactions: FinanceTransaction[];
  contacts: FinanceContact[];
  actionHistory: FinanceActionHistoryEntry[];
  budgets?: FinanceBudget[];
  bills?: FinanceBill[];
  goals?: FinancialGoal[];
}

export type FinanceAction =
  | 'highlight_balance'
  | 'money_sent'
  | 'show_transactions'
  | 'show_budget'
  | 'show_goals'
  | 'bill_paid'
  | 'expense_added'
  | 'show_stock_quote'
  | 'stock_purchased'
  | 'show_portfolio'
  | null;

export interface FinanceAppToolOutput {
  type: 'app';
  appName: 'finance';
  props?: {
    action?: FinanceAction;
    state?: FinanceState;
    transaction?: FinanceTransaction;
  };
}

// Legacy Banking types (kept for backwards compatibility)
export interface BankingTransaction {
  id: string;
  description: string;
  amount: number;
  date: string;
  recipient?: string;
}

export interface BankingContact {
  id: string;
  name: string;
  avatarColor: string;
}

export interface BankingActionHistoryEntry {
  id: string;
  action: string;
  description: string;
  timestamp: string;
}

export interface BankingState {
  balance: number;
  transactions: BankingTransaction[];
  contacts: BankingContact[];
  actionHistory: BankingActionHistoryEntry[];
}

export type BankingAction = 'highlight_balance' | 'money_sent' | 'show_transactions' | null;

export interface BankingAppToolOutput {
  type: 'app';
  appName: 'banking';
  props?: {
    action?: BankingAction;
    state?: BankingState;
    transaction?: BankingTransaction;
  };
}

export type ToolOutput =
  | TextToolOutput
  | ImageToolOutput
  | VideoToolOutput
  | PdfToolOutput
  | ButtonToolOutput
  | BargeinToolOutput
  | AppToolOutput
  | FinanceAppToolOutput
  | BankingAppToolOutput
  | CardToolOutput; 