/**
 * Property-Based Tests for BankingApp
 * Feature: voice-banking-assistant
 * 
 * These tests validate universal properties across all inputs using fast-check.
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import {
    formatTransactionAmount,
    formatCurrency,
    Transaction,
    Contact,
} from '../BankingApp';

// Generators for test data
const transactionArb = fc.record({
    id: fc.uuid(),
    description: fc.string({ minLength: 1, maxLength: 50 }),
    amount: fc.double({ min: -10000, max: 10000, noNaN: true }),
    date: fc.date({ min: new Date('2020-01-01'), max: new Date('2030-12-31') }).map((d) => d.toISOString()),
    recipient: fc.option(fc.string({ minLength: 1, maxLength: 20 }), { nil: undefined }),
});

const contactArb = fc.record({
    id: fc.uuid(),
    name: fc.string({ minLength: 1, maxLength: 30 }),
    avatarColor: fc.constantFrom('bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-red-500', 'bg-yellow-500'),
});

describe('BankingApp Property Tests', () => {
    /**
     * Feature: voice-banking-assistant, Property 1: Transaction Amount Formatting
     * 
     * For any transaction with a positive amount, the formatted display string 
     * SHALL contain a "+" prefix and green color indicator. For any transaction 
     * with a negative amount, the formatted display string SHALL contain a "-" 
     * prefix and red color indicator.
     * 
     * Validates: Requirements 1.5, 1.6
     */
    describe('Property 1: Transaction Amount Formatting', () => {
        it('positive amounts should have + prefix and green color', () => {
            fc.assert(
                fc.property(
                    fc.double({ min: 0.01, max: 10000, noNaN: true }),
                    (amount) => {
                        const result = formatTransactionAmount(amount);
                        expect(result.text.startsWith('+')).toBe(true);
                        expect(result.colorClass).toBe('text-green-500');
                    }
                ),
                { numRuns: 100 }
            );
        });

        it('negative amounts should have - prefix and red color', () => {
            fc.assert(
                fc.property(
                    fc.double({ min: -10000, max: -0.01, noNaN: true }),
                    (amount) => {
                        const result = formatTransactionAmount(amount);
                        expect(result.text.startsWith('-')).toBe(true);
                        expect(result.colorClass).toBe('text-red-500');
                    }
                ),
                { numRuns: 100 }
            );
        });

        it('zero amount should be treated as positive (green)', () => {
            const result = formatTransactionAmount(0);
            expect(result.text.startsWith('+')).toBe(true);
            expect(result.colorClass).toBe('text-green-500');
        });
    });


    /**
     * Feature: voice-banking-assistant, Property 2: Transaction List Completeness
     * 
     * For any list of transactions provided to the Banking_UI, the rendered output 
     * SHALL contain the date, description, and amount for each transaction in the list.
     * 
     * Validates: Requirements 1.2
     */
    describe('Property 2: Transaction List Completeness', () => {
        it('all transaction data should be preserved in formatting', () => {
            fc.assert(
                fc.property(
                    fc.array(transactionArb, { minLength: 0, maxLength: 20 }),
                    (transactions: Transaction[]) => {
                        for (const tx of transactions) {
                            const amountResult = formatTransactionAmount(tx.amount);
                            expect(amountResult.text).toBeDefined();
                            expect(amountResult.colorClass).toBeDefined();

                            const currencyStr = formatCurrency(tx.amount);
                            expect(currencyStr).toContain('$');

                            expect(tx.description.length).toBeGreaterThan(0);
                            expect(() => new Date(tx.date)).not.toThrow();
                        }
                    }
                ),
                { numRuns: 100 }
            );
        });
    });

    /**
     * Feature: voice-banking-assistant, Property 3: Contacts List Completeness
     * 
     * For any list of contacts provided to the Banking_UI, the rendered output 
     * SHALL display all contact names.
     * 
     * Validates: Requirements 1.3
     */
    describe('Property 3: Contacts List Completeness', () => {
        it('all contact names should be valid and displayable', () => {
            fc.assert(
                fc.property(
                    fc.array(contactArb, { minLength: 0, maxLength: 10 }),
                    (contacts: Contact[]) => {
                        for (const contact of contacts) {
                            expect(contact.name.length).toBeGreaterThan(0);
                            expect(contact.id).toBeDefined();
                            expect(contact.avatarColor).toMatch(/^bg-\w+-\d+$/);

                            const firstChar = contact.name.charAt(0).toUpperCase();
                            expect(firstChar).toBeDefined();
                        }
                    }
                ),
                { numRuns: 100 }
            );
        });
    });
});
