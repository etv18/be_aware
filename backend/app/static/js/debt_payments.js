// Every payment on every debt (read only). Markup: templates/debt_payments.html
import { bindList, formatDate, money, source } from './common.js';

bindList({
  path: '/debt_payments',
  open: (row) => { if (row.debt_id) location.href = `/debts/${row.debt_id}`; }, // double click: the debt it belongs to
  cells: (row) => ({
    person: row.person_name || '–',
    meta: `${source(row)} · ${formatDate(row.created_at)}`,
    source: source(row),
    date: formatDate(row.created_at),
    amount: money(row.amount),
  }),
});
