import { money, toNumber } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { manager } from '../domain/resources.js';
import { listPage } from './list-page.js';
import { button, statCards } from './widgets.js';

listPage({
  resource: 'bank-accounts',
  title: 'Bank accounts',
  subtitle: 'Where your money sits.',
  columns: columns.bankAccounts,
  newLabel: 'New account',
  headerActions: button('Ledger', { href: '/bank_transaction_ledger/index', glyph: 'book-open' }),
  noFilters: true,
  summary: (meta, rows) => statCards([
    { label: 'In all accounts', value: money(rows.reduce((sum, r) => sum + toNumber(r.amount_available), 0)) },
    { label: 'Accounts', value: rows.length },
  ]),
  actions: [
    { name: 'transfer', icon: 'arrow-left-right', label: 'Transfer', show: (r) => r.is_active },
  ],
  handlers: {
    open: (row) => { location.href = `/bank_accounts/associated_records/${row.id}`; },
    transfer: (row, { reload }) => manager('bank-transfers', { onChange: reload, ctx: { fromId: row.id, fromName: row.nick_name } }).create(),
  },
});
