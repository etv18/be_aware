// The expenses page. The markup is in templates/expenses.html; this file loads the data, fills it in and reacts to clicks.
import { $, bindList, formatDate, idOrNull, money, nowInputValue, recordForm, setStats, source, toInputValue } from './common.js';
import { yearlyChart } from './chart.js';

const refresh = () => { list.reload(); chart.reload(); };

// ------------------------------------------------------------------ the new / edit form
const form = recordForm($('#record-dialog'), {
  path: '/expenses',
  noun: 'expense',
  selects: {
    expense_category_id: ['expense_categories', 'display_name', 'Choose a category'],
    bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'],
    credit_card_id: ['credit_cards', 'nick_name', 'Choose a card'],
  },
  defaults: (options) => ({
    amount: '', description: '', method: 'cash', created_at: nowInputValue(),
    expense_category_id: options.expense_categories[0]?.id ?? '', bank_account_id: '', credit_card_id: '',
  }),
  fromRecord: (r) => ({
    amount: r.amount, description: r.description, created_at: toInputValue(r.created_at),
    expense_category_id: r.expense_category_id ?? '', method: r.is_cash ? 'cash' : r.credit_card_id ? 'card' : 'bank',
    bank_account_id: r.bank_account_id ?? '', credit_card_id: r.credit_card_id ?? '',
  }),
  toBody: (v) => ({
    amount: v.amount,
    description: v.description,
    created_at: v.created_at || null,
    expense_category_id: idOrNull(v.expense_category_id),
    is_cash: v.method === 'cash',
    bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
    credit_card_id: v.method === 'card' ? idOrNull(v.credit_card_id) : null,
  }),
  onSaved: refresh,
});

// ------------------------------------------------------------------ the list
const list = bindList({
  path: '/expenses',
  form,
  noun: 'expense',
  undo: 'The money goes back to where it came from.',
  onDeleted: refresh,
  empty: { text: 'No expenses this month. Use “New expense” to add one.' },
  // what each cell of a row shows (a record of the API -> text)
  cells: (row) => ({
    description: row.description,
    meta: [row.expense_category_name, formatDate(row.created_at)].filter(Boolean).join(' · '), // the line under the description on a phone
    category: row.expense_category_name || '–',
    source: source(row),
    date: formatDate(row.created_at),
    amount: money(row.amount),
  }),
  onData: ({ meta }) => setStats({
    total: { text: money(meta.total), hint: `${meta.count} expense${meta.count === 1 ? '' : 's'}` },
    limit: money(meta.budget?.limit),
    spent: money(meta.budget?.spent),
    left: { text: money(meta.budget?.left), negative: Number(meta.budget?.left) < 0 },
  }),
});

const chart = yearlyChart({ model: 'expenses', label: 'Expenses', color: 'c-expenses' });
