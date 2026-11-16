// The incomes page. Markup: templates/incomes.html
import { $, bindList, formatDate, idOrNull, money, nowInputValue, recordForm, setStats, source, toInputValue } from './common.js';
import { yearlyChart } from './chart.js';

const refresh = () => { list.reload(); chart.reload(); };

const form = recordForm($('#record-dialog'), {
  path: '/incomes',
  noun: 'income',
  selects: { bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'] },
  defaults: () => ({ amount: '', description: '', method: 'cash', created_at: nowInputValue(), bank_account_id: '' }),
  fromRecord: (r) => ({
    amount: r.amount, description: r.description ?? '', created_at: toInputValue(r.created_at),
    method: r.is_cash ? 'cash' : 'bank', bank_account_id: r.bank_account_id ?? '',
  }),
  toBody: (v) => ({
    amount: v.amount,
    description: v.description || null,
    created_at: v.created_at || null,
    is_cash: v.method === 'cash',
    bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
  }),
  onSaved: refresh,
});

const list = bindList({
  path: '/incomes',
  form,
  noun: 'income',
  onDeleted: refresh,
  empty: { text: 'No incomes this month. Use “New income” to add one.' },
  cells: (row) => ({
    description: row.description || 'No description',
    meta: `${source(row)} · ${formatDate(row.created_at)}`,
    source: source(row),
    date: formatDate(row.created_at),
    amount: money(row.amount),
  }),
  onData: ({ meta }) => setStats({ total: { text: money(meta.total), hint: `${meta.count} record${meta.count === 1 ? '' : 's'}` } }),
});

const chart = yearlyChart({ model: 'incomes', label: 'Income', color: 'c-incomes' });
