// The cash ledger page. Markup: templates/cash_ledger.html
// The ledger is written by the money services; the only thing you add by hand is an adjustment (and you can delete those).
import { $, bindList, formatDateTime, money, nowInputValue, recordForm, setStats, signed, titleCase } from './common.js';

const form = recordForm($('#record-dialog'), {
  path: '/cash_ledger',
  noun: 'adjustment',
  title: () => 'Cash adjustment',
  defaults: () => ({ amount: '', created_at: nowInputValue() }),
  toBody: (v) => ({ amount: v.amount, created_at: v.created_at || null }),
  onSaved: () => list.reload(),
});

const list = bindList({
  path: '/cash_ledger',
  form,
  noun: 'adjustment',
  cells: (row) => ({
    reference: row.reference_code,
    meta: `${titleCase(row.type)} · ${formatDateTime(row.created_at)}`,
    type: titleCase(row.type),
    date: formatDateTime(row.created_at),
    amount: signed(row.amount),
    delete: { show: row.is_adjustment },
  }),
  onData: ({ meta }) => setStats({ cash: money(meta.balance) }),
});
