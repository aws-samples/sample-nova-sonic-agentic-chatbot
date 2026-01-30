'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Wallet,
    ArrowUpRight,
    ArrowDownLeft,
    TrendingUp,
    Receipt,
    Target,
    PiggyBank,
    Lightbulb,
    User
} from 'lucide-react';

// TypeScript interfaces for finance data models
export interface Transaction {
    id: string;
    description: string;
    amount: number;
    date: string;
    recipient?: string;
    category?: string;
}

export interface Contact {
    id: string;
    name: string;
    avatarColor: string;
}

export interface ActionHistoryEntry {
    id: string;
    action: string;
    description: string;
    timestamp: string;
}

export interface Budget {
    id: string;
    category: string;
    limit: number;
    spent: number;
    month: string;
}

export interface Bill {
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
    transactions: Transaction[];
    contacts: Contact[];
    actionHistory: ActionHistoryEntry[];
    budgets?: Budget[];
    bills?: Bill[];
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

export interface FinanceAppProps {
    action?: FinanceAction;
    state?: FinanceState;
    transaction?: Transaction;
    isAgentSpeaking?: boolean;
}

// Suggested actions for users to try
const SUGGESTED_ACTIONS = [
    { icon: Wallet, text: "What's my balance?", category: "Account" },
    { icon: ArrowUpRight, text: "Send $50 to Alice", category: "Transfer" },
    { icon: ArrowDownLeft, text: "Show my transactions", category: "History" },
    { icon: Receipt, text: "Check my budget", category: "Budget" },
    { icon: TrendingUp, text: "Get Apple stock price", category: "Stocks" },
    { icon: TrendingUp, text: "Buy 5 shares of Tesla", category: "Invest" },
    { icon: PiggyBank, text: "Show my portfolio", category: "Invest" },
    { icon: Target, text: "How are my savings goals?", category: "Goals" },
];

// Utility functions
export function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(Math.abs(amount));
}

export function formatTransactionAmount(amount: number): { text: string; colorClass: string } {
    if (amount >= 0) {
        return { text: `+${formatCurrency(amount)}`, colorClass: 'text-green-500' };
    }
    return { text: `-${formatCurrency(amount)}`, colorClass: 'text-red-500' };
}

export function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export function formatTimestamp(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// SuggestedActions Component
interface SuggestedActionsProps {
    shouldCollapse?: boolean;
}

function SuggestedActions({ shouldCollapse = false }: SuggestedActionsProps) {
    const [isExpanded, setIsExpanded] = useState(true);

    // Collapse when action is performed
    useEffect(() => {
        if (shouldCollapse) {
            setIsExpanded(false);
        }
    }, [shouldCollapse]);

    return (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 rounded-2xl shadow-lg overflow-hidden border border-blue-100 dark:border-slate-700">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-blue-100/50 dark:hover:bg-slate-800/50 transition-colors duration-200"
            >
                <div className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-amber-500" />
                    <h3 className="font-semibold text-slate-900 dark:text-white">Try saying...</h3>
                </div>
                <motion.span
                    animate={{ rotate: isExpanded ? 180 : 0 }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                    className="text-slate-500"
                >
                    ▼
                </motion.span>
            </button>
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeOut" }}
                        className="px-4 pb-4"
                    >
                        <div className="grid grid-cols-1 gap-2">
                            {SUGGESTED_ACTIONS.map((action, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.2, delay: index * 0.05 }}
                                    className="flex items-center gap-3 p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all duration-200 cursor-default"
                                >
                                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                                        <action.icon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
                                            "{action.text}"
                                        </p>
                                    </div>
                                    <span className="text-xs px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 rounded-full">
                                        {action.category}
                                    </span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}


// BalanceCard Component
interface BalanceCardProps {
    balance: number;
    savingsBalance?: number;
    highlight?: boolean;
    isPulsing?: boolean;
}

function BalanceCard({ balance, savingsBalance, highlight = false, isPulsing = false }: BalanceCardProps) {
    return (
        <motion.div
            className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-2xl relative overflow-hidden border border-slate-700/50"
            animate={highlight ? { scale: [1, 1.02, 1], boxShadow: ['0 0 0 0 rgba(59, 130, 246, 0)', '0 0 20px 4px rgba(59, 130, 246, 0.4)', '0 0 0 0 rgba(59, 130, 246, 0)'] } : {}}
            transition={{ duration: 0.6, ease: "easeOut" }}
        >
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
            {isPulsing && (
                <motion.div
                    className="absolute inset-0 bg-blue-500/20 rounded-2xl"
                    animate={{ opacity: [0, 0.4, 0], scale: [0.95, 1.02, 0.95] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                />
            )}
            <div className="flex justify-between items-start relative z-10">
                <div>
                    <p className="text-slate-400 text-sm font-medium mb-1">Checking</p>
                    <motion.p
                        className="text-3xl font-bold tracking-tight"
                        animate={highlight ? { color: ['#ffffff', '#60a5fa', '#ffffff'] } : isPulsing ? { scale: [1, 1.02, 1] } : {}}
                        transition={isPulsing ? { duration: 1.5, repeat: Infinity, ease: "easeInOut" } : { duration: 0.6 }}
                    >
                        {formatCurrency(balance)}
                    </motion.p>
                </div>
                {savingsBalance !== undefined && (
                    <div className="text-right">
                        <p className="text-slate-400 text-sm font-medium mb-1">Savings</p>
                        <p className="text-xl font-semibold text-emerald-400">
                            {formatCurrency(savingsBalance)}
                        </p>
                    </div>
                )}
            </div>
            <p className="text-slate-500 text-xs mt-3 relative z-10">Available Balance</p>
        </motion.div>
    );
}

// TransactionList Component
interface TransactionListProps {
    transactions: Transaction[];
    highlightLatest?: boolean;
}

function TransactionList({ transactions, highlightLatest = false }: TransactionListProps) {
    // Sort transactions by date (newest first)
    const sortedTransactions = [...transactions].sort(
        (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    );

    return (
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg overflow-hidden border border-slate-100 dark:border-slate-800">
            <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
                <h3 className="font-semibold text-slate-900 dark:text-white">Recent Transactions</h3>
            </div>
            <div className="max-h-64 overflow-y-auto">
                <AnimatePresence mode="popLayout">
                    {sortedTransactions.slice(0, 6).map((transaction, index) => {
                        const { text, colorClass } = formatTransactionAmount(transaction.amount);
                        const isLatest = index === 0 && highlightLatest;
                        return (
                            <motion.div
                                key={transaction.id}
                                layout
                                initial={{ opacity: 0, x: -20 }}
                                animate={{
                                    opacity: 1,
                                    x: 0,
                                    backgroundColor: isLatest ? 'rgba(59, 130, 246, 0.1)' : 'transparent'
                                }}
                                exit={{ opacity: 0, x: 20 }}
                                transition={{ duration: 0.3 }}
                                className="px-6 py-4 flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 last:border-b-0 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                            >
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-slate-900 dark:text-white truncate">{transaction.description}</p>
                                    <div className="flex items-center gap-2">
                                        <p className="text-sm text-slate-500 dark:text-slate-400">{formatDate(transaction.date)}</p>
                                        {transaction.category && (
                                            <span className="text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-500 rounded-full">
                                                {transaction.category}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <p className={`font-semibold ${colorClass} ml-4`}>{text}</p>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
                {transactions.length === 0 && (
                    <div className="px-6 py-8 text-center text-slate-500">No transactions yet</div>
                )}
            </div>
        </div>
    );
}

// ContactsList Component
interface ContactsListProps {
    contacts: Contact[];
}

function ContactsList({ contacts }: ContactsListProps) {
    return (
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg p-6 border border-slate-100 dark:border-slate-800">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Quick Send</h3>
            <div className="flex gap-4 overflow-x-auto pb-2">
                {contacts.map((contact, index) => (
                    <motion.div
                        key={contact.id}
                        className="flex flex-col items-center min-w-[60px]"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                        <motion.div
                            className={`w-12 h-12 rounded-full flex items-center justify-center text-white ${contact.avatarColor} shadow-md`}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <User className="w-6 h-6" />
                        </motion.div>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 text-center truncate w-full">{contact.name}</p>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}

// ActionHistory Component
interface ActionHistoryProps {
    actionHistory: ActionHistoryEntry[];
}

function ActionHistory({ actionHistory }: ActionHistoryProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const sortedHistory = [...actionHistory].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    return (
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg overflow-hidden border border-slate-100 dark:border-slate-800">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full px-6 py-4 flex items-center justify-between border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors bg-slate-50/50 dark:bg-slate-800/50"
            >
                <h3 className="font-semibold text-slate-900 dark:text-white">Action History</h3>
                <motion.span animate={{ rotate: isExpanded ? 180 : 0 }} className="text-slate-500">▼</motion.span>
            </button>
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="max-h-48 overflow-y-auto"
                    >
                        {sortedHistory.map((entry, index) => (
                            <div key={entry.id} className="px-6 py-3 border-b border-slate-50 dark:border-slate-800/50 last:border-b-0">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs font-mono bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-2 py-1 rounded-md">{entry.action}</span>
                                    <span className="text-xs text-slate-400">{formatTimestamp(entry.timestamp)}</span>
                                </div>
                                <p className="text-sm text-slate-700 dark:text-slate-300 mt-1">{entry.description}</p>
                            </div>
                        ))}
                        {sortedHistory.length === 0 && (
                            <div className="px-6 py-6 text-center text-slate-500 text-sm">No actions recorded yet</div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

// VoiceAgentIndicator Component
interface VoiceAgentIndicatorProps {
    isActive: boolean;
}

function VoiceAgentIndicator({ isActive }: VoiceAgentIndicatorProps) {
    if (!isActive) return null;
    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-2xl px-4 py-3 mb-4 shadow-sm"
        >
            <div className="flex items-center gap-1">
                {[0, 1, 2, 3].map((i) => (
                    <motion.div
                        key={i}
                        className="w-1 h-5 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full"
                        animate={{ scaleY: [0.3, 1, 0.3] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.1, ease: "easeInOut" }}
                    />
                ))}
            </div>
            <span className="text-sm text-blue-600 dark:text-blue-400 font-medium">Agent speaking...</span>
        </motion.div>
    );
}

// Default empty state
const defaultState: FinanceState = {
    balance: 0,
    savingsBalance: 0,
    transactions: [],
    contacts: [],
    actionHistory: [],
    budgets: [],
    bills: [],
    goals: [],
};

// Main FinanceApp Component
export function FinanceApp({ action, state = defaultState, transaction, isAgentSpeaking = false }: FinanceAppProps) {
    const [highlightBalance, setHighlightBalance] = useState(false);
    const [highlightTransaction, setHighlightTransaction] = useState(false);
    const [isPulsingBalance, setIsPulsingBalance] = useState(false);
    const [hasPerformedAction, setHasPerformedAction] = useState(false);

    useEffect(() => {
        if (action) {
            // Collapse suggestions when any action is performed
            setHasPerformedAction(true);
        }

        if (action === 'highlight_balance') {
            setHighlightBalance(true);
            setIsPulsingBalance(true);
            const timer = setTimeout(() => {
                setHighlightBalance(false);
                setIsPulsingBalance(false);
            }, 2000);
            return () => clearTimeout(timer);
        }
        if (action === 'money_sent' || action === 'bill_paid' || action === 'expense_added' || action === 'stock_purchased') {
            setHighlightBalance(true);
            setHighlightTransaction(true);
            const timer = setTimeout(() => {
                setHighlightBalance(false);
                setHighlightTransaction(false);
            }, 1000);
            return () => clearTimeout(timer);
        }
    }, [action, transaction]);

    return (
        <div className="w-full max-w-md mx-auto space-y-4 p-4">
            <AnimatePresence>
                <VoiceAgentIndicator isActive={isAgentSpeaking} />
            </AnimatePresence>
            <SuggestedActions shouldCollapse={hasPerformedAction} />
            <BalanceCard
                balance={state.balance}
                savingsBalance={state.savingsBalance}
                highlight={highlightBalance}
                isPulsing={isPulsingBalance}
            />
            <ContactsList contacts={state.contacts} />
            <TransactionList transactions={state.transactions} highlightLatest={highlightTransaction} />
            <ActionHistory actionHistory={state.actionHistory} />
        </div>
    );
}

export default FinanceApp;
