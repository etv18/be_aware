// The debts page. Markup: templates/debts.html. (loans.js is the same page for money you lent.)
import { $, bindList, formatDate, idOrNull, money, nowInputValue, recordForm, setStats, source, toInputValue } from './common.js';
import { yearlyChart } from './chart.js';
import { paymentForm } from './forms.js';

const refresh = () => { list.reload(); chart.reload(); };

const form = recordForm($('#record-dialog'), {
  path: '/debts',
  noun: 'debt',
  selects: { bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'] },
  defaults: () => ({
    person_name: '', amount: '', description: '', created_at: nowInputValue(), method: 'cash',
    bank_account_id: '', mark_paid: false,
  }),
  fromRecord: (r) => ({
    person_name: r.person_name, amount: r.amount, description: r.description ?? '', created_at: toInputValue(r.created_at),
    method: r.is_cash ? 'cash' : r.bank_account_id ? 'bank' : 'none',
    bank_account_id: r.bank_account_id ?? '', mark_paid: !r.is_active,
  }),
  toBody: (v, record) => ({
    person_name: v.person_name,
    amount: v.amount,
    description: v.description || null,
    created_at: v.created_at || null,
    is_cash: v.method === 'cash',
    bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
    ...(record ? { is_active: !v.mark_paid } : {}), // only when editing: "mark as paid" closes the debt by hand
  }),
  onSaved: refresh,
});

const payment = paymentForm({ kind: 'debt', onSaved: refresh });

const list = bindList({
  path: '/debts',
  form,
  noun: 'debt',
  undo: 'Its payments are removed too.',
  onDeleted: refresh,
  open: (row) => { location.href = `/debts/${row.id}`; }, // double click
  handlers: { pay: (row) => payment.create(row) },
  cells: (row) => ({
    person: row.person_name,
    description: { text: row.description, show: Boolean(row.description) },
    status: row.is_active ? 'Active' : { text: 'Paid', class: 'tag-positive' },
    source: source(row),
    date: formatDate(row.created_at),
    paid: money(row.total_paid),
    remaining: { text: money(row.remaining_amount), class: row.is_active ? 'font-medium' : 'text-muted' },
    amount: money(row.amount),
    pay: { show: row.is_active },
  }),
  onData: ({ meta }) => setStats({ remaining: money(meta.remaining), active: meta.actives ?? meta.active ?? 0, paid: meta.paids ?? meta.paid ?? 0 }),
});

const chart = yearlyChart({ model: 'debts', label: 'Debts', color: 'c-debts' });
