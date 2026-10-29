import { money } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';
import { statCards } from './widgets.js';

listPage({
  resource: 'cash-adjustments',
  listPath: '/cashledger',
  title: 'Cash ledger',
  subtitle: 'Every movement of the cash you hold.',
  columns: columns.cashLedger,
  newLabel: 'Adjust cash',
  placeholder: 'Search reference or type…',
  readOnly: true,
  canCreate: true,
  summary: (meta) => statCards([{ label: 'Cash on hand', value: money(meta.balance) }]),
  actions: [{ name: 'delete', icon: 'trash-2', label: 'Delete adjustment', danger: true, show: (r) => r.is_adjustment }],
  handlers: { delete: (row, { records }) => records.remove(row) },
});
