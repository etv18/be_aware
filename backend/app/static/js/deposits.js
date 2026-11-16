// The deposits page. Markup: templates/deposits.html
import { $, bindList, formatDate, idOrNull, money, nowInputValue, recordForm, setStats, toInputValue } from './common.js';
import { yearlyChart } from './chart.js';

const refresh = () => { list.reload(); chart.reload(); };

const form = recordForm($('#record-dialog'), {
  path: '/deposits',
  noun: 'deposit',
  selects: { bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'] },
  defaults: () => ({ amount: '', description: '', created_at: nowInputValue(), bank_account_id: '' }),
  fromRecord: (r) => ({ amount: r.amount, description: r.description ?? '', created_at: toInputValue(r.created_at), bank_account_id: r.bank_account_id ?? '' }),
  toBody: (v) => ({ amount: v.amount, bank_account_id: idOrNull(v.bank_account_id), description: v.description || null, created_at: v.created_at || null }),
  onSaved: refresh,
});

const list = bindList({
  path: '/deposits',
  form,
  noun: 'deposit',
  undo: 'The money goes back to cash.',
  onDeleted: refresh,
  cells: (row) => ({
    description: row.description || 'Deposit',
    meta: [row.bank_account_name, formatDate(row.created_at)].filter(Boolean).join(' · '),
    account: row.bank_account_name || '–',
    date: formatDate(row.created_at),
    amount: money(row.amount),
  }),
  onData: ({ meta }) => setStats({ total: { text: money(meta.total), hint: `${meta.count} record${meta.count === 1 ? '' : 's'}` } }),
});

const chart = yearlyChart({ model: 'deposits', label: 'Deposits', color: 'c-deposits' });
