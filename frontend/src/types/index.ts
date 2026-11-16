// The shapes of the API. `api.ts` is GENERATED from the backend (npm run gen:api): never edit it by hand.
// This file gives the generated names friendlier ones; add a line here when a page needs another type.
import type { components } from './api';

type Schemas = components['schemas'];

export type Expense = Schemas['ExpenseOut'];
export type ExpenseBody = Schemas['ExpenseIn'];
export type ExpenseListMeta = Schemas['ExpenseListMeta'];

export type Options = Schemas['OptionsOut'];
export type BankAccount = Schemas['BankAccountOut'];
export type CreditCard = Schemas['CreditCardOut'];
export type ExpenseCategory = Schemas['ExpenseCategoryOut'];
export type Dashboard = Schemas['DashboardOut'];
export type Session = Schemas['SessionOut'];
export type YearlyReport = Schemas['YearlyReportOut'];

/** What every success looks like: {"data": ...}, and for lists also {"meta": ...}. */
export type One<T> = { data: T };
export type List<T, M = Schemas['ListMeta']> = { data: T[]; meta: M };
