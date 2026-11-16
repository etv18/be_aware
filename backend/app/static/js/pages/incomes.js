import { loadOptions } from '../core/api.js';
import { money } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';
import { statCards, yearlyChartCard } from './widgets.js';

listPage({
  resource: 'incomes',
  title: 'Incomes',
  subtitle: 'What came in, as cash or into an account.',
  columns: columns.incomes,
  newLabel: 'New income',
  placeholder: 'Search description or account…',
  note: 'Showing this month. Search or pick dates to look further back.',
  summary: (meta) => statCards([
    { label: 'Total', value: money(meta.total), hint: `${meta.count} record${meta.count === 1 ? '' : 's'}` },
  ]),
  after: async (box) => yearlyChartCard(box, { model: 'incomes', label: 'Income', color: 'c-incomes', years: (await loadOptions()).years }),
});
