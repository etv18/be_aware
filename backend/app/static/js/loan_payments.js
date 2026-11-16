// Every payment on every loan (read only). Markup: templates/loan_payments.html
import { bindList, formatDate, money, source } from './common.js';

bindList({
  path: '/loan_payments',
  open: (row) => { if (row.loan_id) location.href = `/loans/${row.loan_id}`; }, // double click: the loan it belongs to
  cells: (row) => ({
    person: row.person_name || '–',
    meta: `${source(row)} · ${formatDate(row.created_at)}`,
    source: source(row),
    date: formatDate(row.created_at),
    amount: money(row.amount),
  }),
});
