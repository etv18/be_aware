// How each kind of record is shown in a table (see core/table.js for the column options).
import { html } from '../core/html.js';
import { date, dateTime, money, titleCase } from '../core/format.js';
import { icon } from '../core/ui.js';

const dash = html`<span class="text-faint">–</span>`;

const dot = (variable) => html`<span class="dot" style="background: rgb(var(--${variable}))"></span>`;

/** A small grey tag, optionally with a colored dot. */
export const tag = (text, dotVariable) => html`<span class="tag">${dotVariable ? dot(dotVariable) : ''}${text}</span>`;

const amountColumn = (key = 'amount', label = 'Amount', tone = '') => ({
  label, amount: true, align: 'right', render: (r) => html`<span class="font-medium ${tone}">${money(r[key])}</span>`,
});

const dateColumn = (label = 'Date') => ({ label, render: (r) => date(r.created_at), className: 'whitespace-nowrap text-muted' });

/** Where the money came from or went to: cash, an account or a card. */
export function sourceOf(record) {
  if (record.is_cash) return html`<span class="tag tag-positive">${icon('banknote', 'size-3.5')}Cash</span>`;
  if (record.credit_card_name) return html`<span class="inline-flex items-center gap-1.5">${icon('credit-card', 'size-3.5 text-muted')}${record.credit_card_name}</span>`;
  if (record.bank_account_name) return html`<span class="inline-flex items-center gap-1.5">${icon('wallet', 'size-3.5 text-muted')}${record.bank_account_name}</span>`;
  return record.person_name ? tag('No money moved') : dash; // a loan or debt settled in kind
}

const source = (label = 'Paid with') => ({ label, render: sourceOf });

const statusTag = (r) => (r.is_active ? tag('Active', 'c-loans') : html`<span class="tag tag-positive">${icon('check', 'size-3.5')}Paid</span>`);

const accountOnly = (key = 'bank_account_name') => (r) => (r[key] ? html`<span class="inline-flex items-center gap-1.5">${icon('wallet', 'size-3.5 text-muted')}${r[key]}</span>` : dash);

// ------------------------------------------------------------------ money in and out

export const expenses = [
  { label: 'Description', primary: true, render: (r) => html`<span class="block max-w-[26ch] truncate sm:max-w-[34ch]" title="${r.description}">${r.description}</span>` },
  { label: 'Category', render: (r) => (r.expense_category_name ? tag(r.expense_category_name, 'c-expenses') : dash) },
  source('Paid with'),
  dateColumn(),
  amountColumn('amount', 'Amount', 'text-negative'),
];

export const incomes = [
  { label: 'Description', primary: true, render: (r) => r.description || html`<span class="text-muted">No description</span>` },
  source('Received in'),
  dateColumn(),
  amountColumn('amount', 'Amount', 'text-positive'),
];

export const withdrawals = [
  { label: 'Description', primary: true, render: (r) => r.description || html`<span class="text-muted">Withdrawal</span>` },
  { label: 'From account', render: accountOnly() },
  dateColumn(),
  amountColumn(),
];

export const deposits = [
  { label: 'Description', primary: true, render: (r) => r.description || html`<span class="text-muted">Deposit</span>` },
  { label: 'Into account', render: accountOnly() },
  dateColumn(),
  amountColumn(),
];

export const bankTransfers = [
  { label: 'Code', primary: true, className: 'font-mono text-xs', render: (r) => r.code },
  { label: 'From', render: (r) => r.from_bank_account_name || dash },
  { label: 'To', render: (r) => r.to_bank_account_name || dash },
  dateColumn(),
  amountColumn(),
];

export const creditCardPayments = [
  { label: 'Card', primary: true, render: (r) => r.credit_card_name || dash },
  { label: 'Paid from', render: (r) => (r.is_cashback ? tag('Cashback') : accountOnly()(r)) },
  dateColumn(),
  amountColumn('amount', 'Amount', 'text-positive'),
];

// ------------------------------------------------------------------ loans and debts

const obligation = (extraSource) => [
  { label: 'Person', primary: true, render: (r) => html`<span class="font-medium">${r.person_name}</span>${r.description ? html`<span class="block max-w-[28ch] truncate text-xs font-normal text-muted">${r.description}</span>` : ''}` },
  { label: 'Status', render: statusTag },
  extraSource,
  dateColumn(),
  { label: 'Paid', align: 'right', render: (r) => money(r.total_paid) },
  { label: 'Remaining', align: 'right', render: (r) => html`<span class="${r.is_active ? 'font-medium' : 'text-muted'}">${money(r.remaining_amount)}</span>` },
  amountColumn('amount', 'Amount'),
];

export const loans = obligation({ label: 'Lent from', render: sourceOf });
export const debts = obligation({ label: 'Received in', render: sourceOf });

export const loanPayments = [
  { label: 'Person', primary: true, render: (r) => r.person_name || dash },
  { label: 'Received in', render: sourceOf },
  dateColumn(),
  amountColumn('amount', 'Amount', 'text-positive'),
];

export const debtPayments = [
  { label: 'Person', primary: true, render: (r) => r.person_name || dash },
  { label: 'Paid from', render: sourceOf },
  dateColumn(),
  amountColumn('amount', 'Amount', 'text-negative'),
];

// ------------------------------------------------------------------ reference data

export const banks = [
  { label: 'Bank', primary: true, render: (r) => html`<span class="inline-flex items-center gap-2 font-medium">${icon('landmark', 'text-muted')}${r.name}</span>` },
  { label: 'Added', render: (r) => date(r.created_at), className: 'text-muted' },
];

export const bankAccounts = [
  { label: 'Account', primary: true, render: (r) => html`<span class="font-medium">${r.nick_name}</span>${r.account_number ? html`<span class="block font-mono text-xs font-normal text-muted">${r.account_number}</span>` : ''}` },
  { label: 'Bank', render: (r) => r.bank_name || dash },
  { label: 'Status', render: (r) => (r.is_active ? tag('Active', 'c-withdrawals') : tag('Inactive')) },
  { label: 'Added', render: (r) => date(r.created_at), className: 'text-muted' },
  amountColumn('amount_available', 'Balance'),
];

export const creditCards = [
  { label: 'Card', primary: true, render: (r) => html`<span class="font-medium">${r.nick_name}</span>` },
  { label: 'Bank', render: (r) => r.bank_name || dash },
  { label: 'Limit', align: 'right', render: (r) => money(r.limit) },
  {
    label: 'Used', align: 'right',
    render: (r) => {
      const share = Number(r.limit) > 0 ? Math.min(100, Math.round((Number(r.used) / Number(r.limit)) * 100)) : 0;
      return html`<div class="ml-auto w-28">
        <div class="flex justify-between text-xs"><span>${money(r.used)}</span><span class="text-muted">${share}%</span></div>
        <div class="mt-1 h-1 rounded-full bg-sunken"><div class="h-1 rounded-full ${share > 85 ? 'bg-negative' : 'bg-ink'}" style="width: ${share}%"></div></div>
      </div>`;
    },
  },
  amountColumn('amount_available', 'Available'),
];

export const expenseCategories = [
  { label: 'Category', primary: true, render: (r) => html`<span class="inline-flex items-center gap-2 font-medium">${dot('c-expenses')}${r.display_name}</span>` },
  { label: 'Added', render: (r) => date(r.created_at), className: 'text-muted' },
  { label: 'Monthly limit', amount: true, align: 'right', render: (r) => (Number(r.limit) > 0 ? money(r.limit) : html`<span class="text-muted">No limit</span>`) },
];

// ------------------------------------------------------------------ ledgers

const signed = (value) => html`<span class="font-medium ${Number(value) < 0 ? 'text-negative' : 'text-positive'}">${Number(value) > 0 ? '+' : ''}${money(value)}</span>`;

export const cashLedger = [
  { label: 'Reference', primary: true, className: 'font-mono text-xs', render: (r) => r.reference_code },
  { label: 'Type', render: (r) => tag(titleCase(r.type)) },
  { label: 'Date', render: (r) => dateTime(r.created_at), className: 'whitespace-nowrap text-muted' },
  { label: 'Amount', amount: true, align: 'right', render: (r) => signed(r.amount) },
];

const productLedger = (nameKey, nameLabel) => [
  { label: 'Reference', primary: true, className: 'font-mono text-xs', render: (r) => r.reference_code },
  { label: nameLabel, render: (r) => r[nameKey] || dash },
  { label: 'Type', render: (r) => tag(titleCase(r.transaction_type)) },
  { label: 'Date', render: (r) => dateTime(r.created_at), className: 'whitespace-nowrap text-muted' },
  { label: 'Before', align: 'right', render: (r) => money(r.before_balance), hideOnMobile: true },
  { label: 'After', align: 'right', render: (r) => money(r.after_balance), hideOnMobile: true },
  { label: 'Amount', amount: true, align: 'right', render: (r) => signed(r.amount) },
];

export const bankLedger = productLedger('bank_account_name', 'Account');
export const cardLedger = productLedger('credit_card_name', 'Card');
