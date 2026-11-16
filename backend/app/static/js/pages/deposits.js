import { loadOptions } from '../core/api.js';
import { money } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';
import { statCards, yearlyChartCard } from './widgets.js';

listPage({
  resource: 'deposits',
  title: 'Deposits',
  subtitle: 'Cash you put into a bank account.',
  columns: columns.deposits,
  newLabel: 'New deposit',
  placeholder: 'Search description or account…',

  summary: (meta) => statCards([
    { label: 'Total', value: money(meta.total), hint: `${meta.count} record${meta.count === 1 ? '' : 's'}` },
  ]),
  after: async (box) => yearlyChartCard(box, { model: 'deposits', label: 'Deposits', color: 'c-deposits', years: (await loadOptions()).years }),
});
