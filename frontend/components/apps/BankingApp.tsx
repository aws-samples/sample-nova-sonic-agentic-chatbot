'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// TypeScript interfaces for banking data models
export interface Transaction {
    id: string;
    description: string;
    amount: number; // Positive = incoming, negative = outgoing
    date: string; // ISO date string
    recipient?: string; // For outgoing transfers
}

export interface Contact {
    id: string;
    name: string;
    avatarColor: string; // Tailwind color class
}

export interface ActionHistoryEntry {
    id: string;
    action: string; // Tool name
    description: string; // Human-readable description
    timestamp: string; // ISO date string
}

export interface BankingState {
    balance: number;
    transactions: Transaction[];
    contacts: Contact[];
    actionHistory: ActionHistoryEntry[];
}

export type BankingAction = 'highlight_balance' | 'money_sent' | 'show_transactions' | null;

export interface BankingAppProps {
    action?: BankingAction;
    state?: BankingState;
    transaction?: Transaction;
    isAgentSpeaking?: boolean;
}

// Utility functions for formatting
export function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(Math.abs(amount));
}

export function formatTransactionAmount(amount: number): { text: string; colorClass: string } {
    if (amount >= 0) {
        return {
            text: `+${formatCurrency(amount)}`,
            colorClass: 'text-green-500',
        };
    }
    return {
        text: `-${formatCurrency(amount)}`,
        colorClass: 'text-red-500',
    };
}

export function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    });
}

export function formatTimestamp(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}


// BalanceCard Component
interface BalanceCardProps {
    balance: number;
    highlight?: boolean;
    isPulsing?: boolean;
}

function BalanceCard({ balance, highlight = false, isPulsing = false }: BalanceCardProps) {
    return (
        <motion.div
            className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-2xl relative overflow-hidden border border-slate-700/50"
            animate={highlight ? { scale: [1, 1.02, 1], boxShadow: ['0 0 0 0 rgba(59, 130, 246, 0)', '0 0 20px 4px rgba(59, 130, 246, 0.4)', '0 0 0 0 rgba(59, 130, 246, 0)'] } : {}}
            transition={{ duration: 0.6, ease: "easeOut" }}
        >
            {/* Subtle gradient overlay for depth */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />

            {/* Pulse animation overlay for check_balance */}
            {isPulsing && (
                <motion.div
                    className="absolute inset-0 bg-blue-500/20 rounded-2xl"
                    animate={{
                        opacity: [0, 0.4, 0],
                        scale: [0.95, 1.02, 0.95],
                    }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            )}
            <p className="text-slate-400 text-sm font-medium mb-1 relative z-10">Current Balance</p>
            <motion.p
                className="text-4xl font-bold tracking-tight relative z-10"
                animate={highlight ? { color: ['#ffffff', '#60a5fa', '#ffffff'] } : isPulsing ? { scale: [1, 1.02, 1] } : {}}
                transition={isPulsing ? { duration: 1.5, repeat: Infinity, ease: "easeInOut" } : { duration: 0.6 }}
            >
                {formatCurrency(balance)}
            </motion.p>
            <p className="text-slate-500 text-xs mt-2 relative z-10">Available</p>
        </motion.div>
    );
}

// TransactionList Component
interface TransactionListProps {
    transactions: Transaction[];
    highlightLatest?: boolean;
}

function TransactionList({ transactions, highlightLatest = false }: TransactionListProps) {
    return (
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg overflow-hidden border border-slate-100 dark:border-slate-800">
            <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
                <h3 className="font-semibold text-slate-900 dark:text-white">Recent Transactions</h3>
            </div>
            <div className="max-h-64 overflow-y-auto">
                <AnimatePresence>
                    {transactions.map((transaction, index) => {
                        const { text, colorClass } = formatTransactionAmount(transaction.amount);
                        const isLatest = index === 0 && highlightLatest;

                        return (
                            <motion.div
                                key={transaction.id}
                                initial={isLatest ? { opacity: 0, x: -20, backgroundColor: 'rgba(59, 130, 246, 0.1)' } : false}
                                animate={{ opacity: 1, x: 0, backgroundColor: isLatest ? 'rgba(59, 130, 246, 0.05)' : 'transparent' }}
                                exit={{ opacity: 0, x: 20 }}
                                transition={{ duration: 0.4, ease: "easeOut" }}
                                className={`px-6 py-4 flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 last:border-b-0 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors duration-200`}
                            >
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-slate-900 dark:text-white truncate">
                                        {transaction.description}
                                    </p>
                                    <p className="text-sm text-slate-500 dark:text-slate-400">
                                        {formatDate(transaction.date)}
                                    </p>
                                </div>
                                <motion.p
                                    className={`font-semibold ${colorClass} ml-4`}
                                    initial={isLatest ? { scale: 1.1 } : false}
                                    animate={{ scale: 1 }}
                                    transition={{ duration: 0.3, delay: 0.2 }}
                                >
                                    {text}
                                </motion.p>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
                {transactions.length === 0 && (
                    <div className="px-6 py-8 text-center text-slate-500">
                        No transactions yet
                    </div>
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
            <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
                {contacts.map((contact, index) => (
                    <motion.div
                        key={contact.id}
                        className="flex flex-col items-center min-w-[60px]"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                        <motion.div
                            className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-lg ${contact.avatarColor} shadow-md`}
                            whileHover={{ scale: 1.1, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
                            whileTap={{ scale: 0.95 }}
                            transition={{ type: "spring", stiffness: 400, damping: 17 }}
                        >
                            {contact.name.charAt(0).toUpperCase()}
                        </motion.div>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 text-center truncate w-full">
                            {contact.name}
                        </p>
                    </motion.div>
                ))}
                {contacts.length === 0 && (
                    <p className="text-slate-500 text-sm">No contacts available</p>
                )}
            </div>
        </div>
    );
}

// ActionHistory Component
interface ActionHistoryProps {
    actionHistory: ActionHistoryEntry[];
}

function ActionHistory({ actionHistory }: ActionHistoryProps) {
    const [isExpanded, setIsExpanded] = useState(true);

    // Sort by timestamp descending (newest first)
    const sortedHistory = [...actionHistory].sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

    return (
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg overflow-hidden border border-slate-100 dark:border-slate-800">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full px-6 py-4 flex items-center justify-between border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors duration-200 bg-slate-50/50 dark:bg-slate-800/50"
            >
                <h3 className="font-semibold text-slate-900 dark:text-white">Action History</h3>
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
                        className="max-h-48 overflow-y-auto"
                    >
                        {sortedHistory.map((entry, index) => (
                            <motion.div
                                key={entry.id}
                                initial={index === 0 ? { opacity: 0, x: -20, backgroundColor: 'rgba(59, 130, 246, 0.1)' } : false}
                                animate={{ opacity: 1, x: 0, backgroundColor: 'transparent' }}
                                transition={{ duration: 0.4, delay: index * 0.05, ease: "easeOut" }}
                                className="px-6 py-3 border-b border-slate-50 dark:border-slate-800/50 last:border-b-0 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors duration-200"
                            >
                                <div className="flex items-center justify-between">
                                    <span className="text-xs font-mono bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-2 py-1 rounded-md border border-slate-200 dark:border-slate-700">
                                        {entry.action}
                                    </span>
                                    <span className="text-xs text-slate-400">
                                        {formatTimestamp(entry.timestamp)}
                                    </span>
                                </div>
                                <p className="text-sm text-slate-700 dark:text-slate-300 mt-1">
                                    {entry.description}
                                </p>
                            </motion.div>
                        ))}
                        {sortedHistory.length === 0 && (
                            <div className="px-6 py-6 text-center text-slate-500 text-sm">
                                No actions recorded yet
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}


// Default empty state
const defaultState: BankingState = {
    balance: 0,
    transactions: [],
    contacts: [],
    actionHistory: [],
};

// VoiceAgentIndicator Component - shows when agent is speaking
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
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="flex items-center gap-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-2xl px-4 py-3 mb-4 shadow-sm"
        >
            <div className="flex items-center gap-1">
                {[0, 1, 2, 3].map((i) => (
                    <motion.div
                        key={i}
                        className="w-1 h-5 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full"
                        animate={{
                            scaleY: [0.3, 1, 0.3],
                        }}
                        transition={{
                            duration: 0.6,
                            repeat: Infinity,
                            delay: i * 0.1,
                            ease: "easeInOut",
                        }}
                    />
                ))}
            </div>
            <span className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                Agent speaking...
            </span>
        </motion.div>
    );
}

// Main BankingApp Component
export function BankingApp({ action, state = defaultState, transaction, isAgentSpeaking = false }: BankingAppProps) {
    const [highlightBalance, setHighlightBalance] = useState(false);
    const [highlightTransaction, setHighlightTransaction] = useState(false);
    const [isPulsingBalance, setIsPulsingBalance] = useState(false);

    // Handle action-based animations
    useEffect(() => {
        if (action === 'highlight_balance') {
            setHighlightBalance(true);
            setIsPulsingBalance(true);
            const timer = setTimeout(() => {
                setHighlightBalance(false);
                setIsPulsingBalance(false);
            }, 2000);
            return () => clearTimeout(timer);
        }
        if (action === 'money_sent') {
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
            <BalanceCard balance={state.balance} highlight={highlightBalance} isPulsing={isPulsingBalance} />
            <ContactsList contacts={state.contacts} />
            <TransactionList
                transactions={state.transactions}
                highlightLatest={highlightTransaction}
            />
            <ActionHistory actionHistory={state.actionHistory} />
        </div>
    );
}

export default BankingApp;
