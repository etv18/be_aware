// Every movement of every credit card (read only). Markup: templates/card_ledger.html
import { bindList, formatDateTime, money, signed, titleCase } from './common.js';

bindList({
  path: '/card_ledger',
  cells: (row) => ({
    reference: row.reference_code,
    meta: `${row.credit_card_name || '–'} · ${formatDateTime(row.created_at)}`,
    card: row.credit_card_name || '–',
    type: titleCase(row.transaction_type),
    date: formatDateTime(row.created_at),
    before: money(row.before_balance),
    after: money(row.after_balance),
    amount: signed(row.amount),
  }),
});
