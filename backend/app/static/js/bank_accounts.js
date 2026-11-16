// The bank accounts page. Markup: templates/bank_accounts.html
import { $, bindList, formatDate, idOrNull, money, recordForm, setStats, sum } from './common.js';
import { transferForm } from './forms.js';

const form = recordForm($('#record-dialog'), {
  path: '/bank_accounts',
  noun: 'bank account',
  selects: { bank_id: ['banks', 'name', 'Choose a bank'] },
  defaults: () => ({ nick_name: '', account_number: '', amount_available: '', bank_id: '' }),
  fromRecord: (r) => ({ nick_name: r.nick_name, account_number: r.account_number ?? '', amount_available: r.amount_available, bank_id: r.bank_id ?? '' }),
  toBody: (v) => ({ nick_name: v.nick_name, account_number: v.account_number || null, amount_available: v.amount_available, bank_id: idOrNull(v.bank_id) }),
  onSaved: () => list.reload(),
});

const transfer = transferForm({ onSaved: () => list.reload() });

const list = bindList({
  path: '/bank_accounts',
  form,
  noun: 'bank account',
  undo: 'It is hidden; its history stays.',
  open: (row) => { location.href = `/bank_accounts/${row.id}`; }, // double click
  handlers: { transfer: (row) => transfer.open(row) },
  cells: (row) => ({
    name: row.nick_name,
    number: { text: row.account_number, show: Boolean(row.account_number) },
    bank: row.bank_name || '–',
    status: row.is_active ? 'Active' : 'Inactive',
    added: formatDate(row.created_at),
    balance: money(row.amount_available),
    transfer: { show: row.is_active }, // the transfer button only on active accounts
  }),
  onData: ({ rows }) => setStats({ total: money(sum(rows, 'amount_available')), count: rows.length }),
});
