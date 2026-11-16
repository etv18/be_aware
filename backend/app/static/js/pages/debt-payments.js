import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';

listPage({
  resource: 'debt-payments',
  title: 'Debt payments',
  subtitle: 'Everything you paid, across all debts.',
  columns: columns.debtPayments,
  placeholder: 'Search person or account…',
  readOnly: true,
  handlers: { open: (row) => { if (row.debt_id) location.href = `/debts/associated/records/${row.debt_id}`; } }, // double click
});
