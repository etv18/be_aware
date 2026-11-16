import { money, toNumber } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { manager } from '../domain/resources.js';
import { listPage } from './list-page.js';
import { button, statCards } from './widgets.js';

listPage({
  resource: 'credit-cards',
  title: 'Credit cards',
  subtitle: 'Limits, what you used and what is left.',
  columns: columns.creditCards,
  newLabel: 'New card',
  headerActions: button('Ledger', { href: '/credit_card_ledger/ledger', glyph: 'book-open' }),
  noFilters: true,
  summary: (meta, rows) => statCards([
    { label: 'Used', value: money(rows.reduce((sum, r) => sum + toNumber(r.used), 0)) },
    { label: 'Available', value: money(rows.reduce((sum, r) => sum + toNumber(r.amount_available), 0)) },
  ]),
  actions: [
    { name: 'pay', icon: 'banknote', label: 'Pay the card', show: (r) => r.is_active },
  ],
  handlers: {
    open: (row) => { location.href = `/credit_cards/associated_records/${row.id}`; },
    pay: (row, { reload }) => manager('credit-card-payments', { onChange: reload, ctx: { cardId: row.id } }).create(),
  },
});
