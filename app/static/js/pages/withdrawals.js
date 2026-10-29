import { loadOptions } from '../core/api.js';
import { money } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';
import { statCards, yearlyChartCard } from './widgets.js';

listPage({
  resource: 'withdrawals',
  title: 'Withdrawals',
  subtitle: 'Money you took out of a bank account as cash.',
  columns: columns.withdrawals,
  newLabel: 'New withdrawal',
  placeholder: 'Search description or account…',

  summary: (meta) => statCards([
    { label: 'Total', value: money(meta.total), hint: `${meta.count} record${meta.count === 1 ? '' : 's'}` },
  ]),
  after: async (box) => yearlyChartCard(box, { model: 'withdrawals', label: 'Withdrawals', color: 'c-withdrawals', years: (await loadOptions()).years }),
});
