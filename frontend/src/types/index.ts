// The shapes of the API. `api.ts` is GENERATED from the backend (npm run gen:api): never edit it by hand.
// This file gives the generated names friendlier ones; add a line here when a page needs another type.
import type { components } from './api';

type Schemas = components['schemas'];

export type Expense = Schemas['ExpenseOut'];
export type ExpenseBody = Schemas['ExpenseIn'];
export type ExpenseListMeta = Schemas['ExpenseListMeta'];

export type Income = Schemas['IncomeOut'];
export type IncomeBody = Schemas['IncomeIn'];
export type CashMovement = Schemas['CashMovementOut'];
export type WithdrawalBody = Schemas['WithdrawalIn'];
export type Bank = Schemas['BankOut'];
export type Loan = Schemas['LoanOut'];
export type LoanBody = Schemas['LoanIn'];
export type LoanUpdate = Schemas['LoanUpdate'];
export type Debt = Schemas['DebtOut'];
export type DebtBody = Schemas['DebtIn'];
export type DebtUpdate = Schemas['DebtUpdate'];
export type Obligation = Loan | Debt;
export type Payment = Schemas['LoanPaymentOut'] | Schemas['DebtPaymentOut'];
export type LoanPayment = Schemas['LoanPaymentOut'];
export type DebtPayment = Schemas['DebtPaymentOut'];
export type CashLedgerRow = Schemas['CashLedgerOut'];
export type BankLedgerRow = Schemas['BankLedgerOut'];
export type CardLedgerRow = Schemas['CardLedgerOut'];
export type RecordsKinds = Schemas['RecordsOut'];
export type BankAccountRecords = Schemas['BankAccountRecordsOut'];
export type CreditCardRecords = Schemas['CreditCardRecordsOut'];
export type ExpenseCategoryRecords = Schemas['ExpenseCategoryRecordsOut'];
export type AccountCashFlow = Schemas['AccountCashFlowOut'];
export type CardYearly = Schemas['CardYearlyOut'];
export type CategoriesMonthly = Schemas['CategoriesMonthlyOut'];
export type CashFlow = Schemas['CashFlowOut'];
export type YearlyAll = Schemas['YearlyAllOut'];

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
