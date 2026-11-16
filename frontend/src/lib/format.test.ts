import { describe, expect, it } from 'vitest';

import { formatDate, idOrNull, money, plural, source, sum, toInputValue } from './format';

describe('money', () => {
  it('writes two decimals and thousands separators', () => {
    expect(money('1234.5')).toBe('1,234.50');
    expect(money(0)).toBe('0.00');
  });
  it('shows a dash when there is nothing to show', () => {
    expect(money(null)).toBe('-');
    expect(money(undefined)).toBe('-');
    expect(money('')).toBe('-');
    expect(money('abc')).toBe('-');
  });
});

describe('dates', () => {
  it('formats an ISO text without moving the day', () => {
    expect(formatDate('2026-10-28T15:41:00')).toBe('Oct 28, 2026');
    expect(formatDate(null)).toBe('-');
  });
  it('makes the value of a datetime-local input', () => {
    expect(toInputValue('2026-10-28T15:41:00')).toBe('2026-10-28T15:41');
    expect(toInputValue()).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/);
  });
});

describe('helpers', () => {
  it('turns a select value into an id', () => {
    expect(idOrNull('')).toBeNull();
    expect(idOrNull('7')).toBe(7);
    expect(idOrNull(null)).toBeNull();
  });
  it('says where the money came from', () => {
    expect(source({ is_cash: true })).toBe('Cash');
    expect(source({ credit_card_name: 'Visa', bank_account_name: 'Checking' })).toBe('Visa');
    expect(source({ bank_account_name: 'Checking' })).toBe('Checking');
    expect(source({ person_name: 'Ana' })).toBe('No money moved');
    expect(source({})).toBe('–');
  });
  it('sums text and numbers, ignoring what is not a number', () => {
    expect(sum(['1.50', 2, 'x', null])).toBe(3.5);
  });
  it('picks the singular only for one', () => {
    expect(plural(1, 'expense')).toBe('expense');
    expect(plural(0, 'expense')).toBe('expenses');
  });
});
