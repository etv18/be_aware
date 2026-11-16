import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';

listPage({
  resource: 'loan-payments',
  title: 'Loan payments',
  subtitle: 'Everything people paid back, across all loans.',
  columns: columns.loanPayments,
  placeholder: 'Search person or account…',
  readOnly: true,
  handlers: { open: (row) => { if (row.loan_id) location.href = `/loans/associated_records/${row.loan_id}`; } }, // double click
});
