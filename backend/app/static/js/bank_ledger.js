// Every movement of every bank account (read only). Markup: templates/bank_ledger.html
import { bindList, formatDateTime, money, signed, titleCase } from './common.js';

bindList({
  path: '/bank_ledger',
  cells: (row) => ({
    reference: row.reference_code,
    meta: `${row.bank_account_name || '–'} · ${formatDateTime(row.created_at)}`,
    account: row.bank_account_name || '–',
    type: titleCase(row.transaction_type),
    date: formatDateTime(row.created_at),
    before: money(row.before_balance),
    after: money(row.after_balance),
    amount: signed(row.amount),
  }),
});
