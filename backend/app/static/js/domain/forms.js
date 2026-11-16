// What each kind of record asks for. Every function takes the select options (banks, accounts, ...) and returns
//   { title(record?), fields, defaults(), fromRecord(record), toBody(values, record) }
// Nothing here knows about the HTML: core/form.js draws it, the API receives the JSON built by toBody().
import { blankToNull, idOrNull, toOptions } from '../core/form.js';
import { nowInputValue, toInputValue } from '../core/format.js';

const accounts = (o) => toOptions(o.bank_accounts, 'nick_name');
const cards = (o) => toOptions(o.credit_cards, 'nick_name');
const banks = (o) => toOptions(o.banks, 'name');

const amount = (label = 'Amount') => ({ name: 'amount', label, type: 'money', required: true, half: true });
const dateField = { name: 'created_at', label: 'Date and time', type: 'datetime', required: true, half: true };
const description = (required = false) => ({ name: 'description', label: 'Description', type: 'text', required });
const dateOrNull = (value) => blankToNull(value);

const METHODS = {
  cash: { value: 'cash', label: 'Cash' },
  bank: { value: 'bank', label: 'Bank account' },
  card: { value: 'card', label: 'Credit card' },
  none: { value: 'none', label: 'No money' },
};
const methods = (...names) => names.map((n) => METHODS[n]);

const methodOf = (record) => (record.is_cash ? 'cash' : record.credit_card_id ? 'card' : record.bank_account_id ? 'bank' : 'none');

const methodFields = (o, ...names) => [
  { name: 'method', label: 'Paid with', type: 'segmented', options: methods(...names) },
  { name: 'bank_account_id', label: 'Bank account', type: 'select', options: accounts(o), blank: 'Choose an account', required: true, when: (v) => v.method === 'bank' },
  ...(names.includes('card')
    ? [{ name: 'credit_card_id', label: 'Credit card', type: 'select', options: cards(o), blank: 'Choose a card', required: true, when: (v) => v.method === 'card' }]
    : []),
];

const productIds = (v) => ({
  bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
  credit_card_id: v.method === 'card' ? idOrNull(v.credit_card_id) : null,
});

// ------------------------------------------------------------------ money in and out

export const expense = (o) => ({
  title: (r) => (r ? 'Edit expense' : 'New expense'),
  fields: [
    amount(),
    dateField,
    { name: 'expense_category_id', label: 'Category', type: 'select', options: toOptions(o.expense_categories, 'display_name'), blank: 'Choose a category', required: true },
    description(true),
    ...methodFields(o, 'cash', 'bank', 'card'),
  ],
  defaults: () => ({ method: 'cash', created_at: nowInputValue(), expense_category_id: o.expense_categories[0]?.id ?? '' }),
  fromRecord: (r) => ({
    amount: r.amount, created_at: toInputValue(r.created_at), expense_category_id: r.expense_category_id ?? '',
    description: r.description, method: methodOf(r), bank_account_id: r.bank_account_id ?? '', credit_card_id: r.credit_card_id ?? '',
  }),
  toBody: (v) => ({
    amount: v.amount, is_cash: v.method === 'cash', expense_category_id: idOrNull(v.expense_category_id),
    description: v.description, created_at: dateOrNull(v.created_at), ...productIds(v),
  }),
});

export const income = (o) => ({
  title: (r) => (r ? 'Edit income' : 'New income'),
  fields: [
    amount(),
    dateField,
    description(),
    { name: 'method', label: 'Received in', type: 'segmented', options: methods('cash', 'bank') },
    { name: 'bank_account_id', label: 'Bank account', type: 'select', options: accounts(o), blank: 'Choose an account', required: true, when: (v) => v.method === 'bank' },
  ],
  defaults: () => ({ method: 'cash', created_at: nowInputValue() }),
  fromRecord: (r) => ({
    amount: r.amount, created_at: toInputValue(r.created_at), description: r.description ?? '',
    method: r.is_cash ? 'cash' : 'bank', bank_account_id: r.bank_account_id ?? '',
  }),
  toBody: (v) => ({
    amount: v.amount, is_cash: v.method === 'cash', description: blankToNull(v.description),
    created_at: dateOrNull(v.created_at), bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
  }),
});

const cashMovement = (name, accountLabel) => (o) => ({
  title: (r) => (r ? `Edit ${name}` : `New ${name}`),
  fields: [
    amount(),
    dateField,
    { name: 'bank_account_id', label: accountLabel, type: 'select', options: accounts(o), blank: 'Choose an account', required: true },
    description(),
  ],
  defaults: () => ({ created_at: nowInputValue() }),
  fromRecord: (r) => ({ amount: r.amount, created_at: toInputValue(r.created_at), bank_account_id: r.bank_account_id ?? '', description: r.description ?? '' }),
  toBody: (v) => ({ amount: v.amount, bank_account_id: idOrNull(v.bank_account_id), description: blankToNull(v.description), created_at: dateOrNull(v.created_at) }),
});

export const withdrawal = cashMovement('withdrawal', 'Withdraw from');
export const deposit = cashMovement('deposit', 'Deposit into');

// ------------------------------------------------------------------ loans and debts

// only on the edit form: closes the record by hand and takes it out of what is left to collect or pay
const markPaid = (help) => ({ name: 'mark_paid', label: 'Mark as paid', help, type: 'switch', editOnly: true });

const person = { name: 'person_name', label: 'Person', type: 'text', required: true, half: true };

export const loan = (o) => ({
  title: (r) => (r ? 'Edit loan' : 'New loan'),
  fields: [
    person, amount(),
    dateField,
    description(),
    ...methodFields(o, 'cash', 'bank', 'card', 'none').map((f) => (f.name === 'method' ? { ...f, label: 'Lent from', help: 'Pick "No money" when you paid for something in kind and no money left your hands.' } : f)),
    markPaid('The person owes you nothing more, even if the payments do not cover the amount.'),
  ],
  defaults: () => ({ method: 'cash', created_at: nowInputValue(), mark_paid: false }),
  fromRecord: (r) => ({
    person_name: r.person_name, amount: r.amount, created_at: toInputValue(r.created_at), description: r.description ?? '',
    method: methodOf(r), bank_account_id: r.bank_account_id ?? '', credit_card_id: r.credit_card_id ?? '', mark_paid: !r.is_active,
  }),
  toBody: (v, record) => ({
    person_name: v.person_name, amount: v.amount, is_cash: v.method === 'cash', description: blankToNull(v.description),
    created_at: dateOrNull(v.created_at), ...productIds(v), ...(record ? { is_active: !v.mark_paid } : {}),
  }),
});

export const debt = (o) => ({
  title: (r) => (r ? 'Edit debt' : 'New debt'),
  fields: [
    person, amount(),
    dateField,
    description(),
    { name: 'method', label: 'Received in', type: 'segmented', options: methods('cash', 'bank', 'none'), help: 'Pick "No money" when someone paid for something in kind and you never received the money.' },
    { name: 'bank_account_id', label: 'Bank account', type: 'select', options: accounts(o), blank: 'Choose an account', required: true, when: (v) => v.method === 'bank' },
    markPaid('You owe nothing more, even if the payments do not cover the amount.'),
  ],
  defaults: () => ({ method: 'cash', created_at: nowInputValue(), mark_paid: false }),
  fromRecord: (r) => ({
    person_name: r.person_name, amount: r.amount, created_at: toInputValue(r.created_at), description: r.description ?? '',
    method: methodOf(r), bank_account_id: r.bank_account_id ?? '', mark_paid: !r.is_active,
  }),
  toBody: (v, record) => ({
    person_name: v.person_name, amount: v.amount, is_cash: v.method === 'cash', description: blankToNull(v.description),
    created_at: dateOrNull(v.created_at), bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
    ...(record ? { is_active: !v.mark_paid } : {}),
  }),
});

/** Payments on a loan (money comes in) or a debt (money goes out). ctx = {parentKey: 'loan_id', parentId} */
const payment = (kind, label) => (o, ctx = {}) => ({
  title: (r) => (r ? `Edit ${kind} payment` : `New ${kind} payment`),
  fields: [
    amount(),
    dateField,
    { name: 'method', label, type: 'segmented', options: methods('cash', 'bank') },
    { name: 'bank_account_id', label: 'Bank account', type: 'select', options: accounts(o), blank: 'Choose an account', required: true, when: (v) => v.method === 'bank' },
  ],
  defaults: () => ({ method: 'cash', created_at: nowInputValue() }),
  fromRecord: (r) => ({ amount: r.amount, created_at: toInputValue(r.created_at), method: r.is_cash ? 'cash' : 'bank', bank_account_id: r.bank_account_id ?? '' }),
  toBody: (v, record) => ({
    amount: v.amount, is_cash: v.method === 'cash', created_at: dateOrNull(v.created_at),
    bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
    ...(record ? {} : { [ctx.parentKey]: ctx.parentId }),
  }),
});

export const loanPayment = payment('loan', 'Received in');
export const debtPayment = payment('debt', 'Paid from');

// ------------------------------------------------------------------ products and reference data

export const bank = () => ({
  title: (r) => (r ? 'Edit bank' : 'New bank'),
  fields: [{ name: 'name', label: 'Bank name', type: 'text', required: true }],
  defaults: () => ({}),
  fromRecord: (r) => ({ name: r.name }),
  toBody: (v) => ({ name: v.name }),
});

export const bankAccount = (o) => ({
  title: (r) => (r ? 'Edit bank account' : 'New bank account'),
  fields: [
    { name: 'nick_name', label: 'Nickname', type: 'text', required: true, half: true },
    { name: 'account_number', label: 'Account number', type: 'text', half: true, placeholder: 'Up to 6 characters' },
    { name: 'amount_available', label: 'Balance', type: 'money', required: true, half: true },
    { name: 'bank_id', label: 'Bank', type: 'select', options: banks(o), blank: 'Choose a bank', required: true, half: true },
  ],
  defaults: () => ({}),
  fromRecord: (r) => ({ nick_name: r.nick_name, account_number: r.account_number ?? '', amount_available: r.amount_available, bank_id: r.bank_id ?? '' }),
  toBody: (v) => ({ nick_name: v.nick_name, account_number: blankToNull(v.account_number), amount_available: v.amount_available, bank_id: idOrNull(v.bank_id) }),
});

export const creditCard = (o) => ({
  title: (r) => (r ? 'Edit credit card' : 'New credit card'),
  fields: [
    { name: 'nick_name', label: 'Nickname', type: 'text', required: true },
    { name: 'limit', label: 'Credit limit', type: 'money', required: true, half: true },
    { name: 'amount_available', label: 'Available credit', type: 'money', required: true, half: true },
    { name: 'bank_id', label: 'Bank', type: 'select', options: banks(o), blank: 'Choose a bank', required: true },
  ],
  defaults: () => ({}),
  fromRecord: (r) => ({ nick_name: r.nick_name, limit: r.limit, amount_available: r.amount_available, bank_id: r.bank_id ?? '' }),
  toBody: (v) => ({ nick_name: v.nick_name, limit: v.limit, amount_available: v.amount_available, bank_id: idOrNull(v.bank_id) }),
});

export const expenseCategory = () => ({
  title: (r) => (r ? 'Edit category' : 'New category'),
  fields: [
    { name: 'name', label: 'Name', type: 'text', required: true, help: 'At least 4 characters.' },
    { name: 'limit', label: 'Monthly limit', type: 'money', help: 'Leave 0 for no limit.' },
  ],
  defaults: () => ({ limit: '0' }),
  fromRecord: (r) => ({ name: r.display_name, limit: r.limit }),
  toBody: (v) => ({ name: v.name, limit: v.limit === '' ? '0' : v.limit }),
});

export const bankTransfer = (o, ctx = {}) => ({
  title: (r) => (r ? 'Edit transfer' : 'New transfer'),
  fields: [
    ...(ctx.fromName ? [] : [{ name: 'from_bank_account_id', label: 'From', type: 'select', options: accounts(o), blank: 'Choose an account', required: true }]),
    amount(),
    dateField,
    { name: 'to_bank_account_id', label: 'To', type: 'select', options: accounts(o), blank: 'Choose an account', required: true },
  ],
  defaults: () => ({ created_at: nowInputValue() }),
  fromRecord: (r) => ({ amount: r.amount, created_at: toInputValue(r.created_at), to_bank_account_id: r.to_bank_account_id ?? '' }),
  toBody: (v, record) => ({
    amount: v.amount, to_bank_account_id: idOrNull(v.to_bank_account_id), created_at: dateOrNull(v.created_at),
    ...(record ? {} : { from_bank_account_id: ctx.fromId ?? idOrNull(v.from_bank_account_id) }),
  }),
});

export const creditCardPayment = (o, ctx = {}) => ({
  title: (r) => (r ? 'Edit card payment' : 'Pay credit card'),
  fields: [
    ...(ctx.cardId ? [] : [{ name: 'credit_card_id', label: 'Credit card', type: 'select', options: cards(o), blank: 'Choose a card', required: true }]),
    amount(),
    dateField,
    { name: 'is_cashback', label: 'Cashback', help: 'Credit added to the card without paying from an account.', type: 'switch' },
    { name: 'bank_account_id', label: 'Pay from', type: 'select', options: accounts(o), blank: 'Choose an account', required: true, when: (v) => !v.is_cashback },
  ],
  defaults: () => ({ created_at: nowInputValue(), is_cashback: false }),
  fromRecord: (r) => ({ amount: r.amount, created_at: toInputValue(r.created_at), is_cashback: r.is_cashback, bank_account_id: r.bank_account_id ?? '' }),
  toBody: (v, record) => ({
    amount: v.amount, is_cashback: v.is_cashback, created_at: dateOrNull(v.created_at),
    bank_account_id: v.is_cashback ? null : idOrNull(v.bank_account_id),
    ...(record ? {} : { credit_card_id: ctx.cardId ?? idOrNull(v.credit_card_id) }),
  }),
});

export const cashAdjustment = () => ({
  title: () => 'Cash adjustment',
  fields: [
    { name: 'amount', label: 'Amount', type: 'money', required: true, half: true, help: 'Positive adds cash, negative takes it away.' },
    dateField,
  ],
  defaults: () => ({ created_at: nowInputValue() }),
  fromRecord: (r) => ({ amount: r.amount, created_at: toInputValue(r.created_at) }),
  toBody: (v) => ({ amount: v.amount, created_at: dateOrNull(v.created_at) }),
});
