import { getData, loadOptions } from '../core/api.js';
import { html } from '../core/html.js';
import { money } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';
import { statCards, yearlyChartCard } from './widgets.js';

listPage({
  resource: 'expenses',
  title: 'Expenses',
  subtitle: 'What you spent, from cash, accounts and cards.',
  columns: columns.expenses,
  newLabel: 'New expense',
  placeholder: 'Search description, category, account…',
  note: 'Showing this month. Search or pick dates to look further back.',
  emptyText: 'No expenses this month.',
  summary: (meta) => statCards([
    { label: 'Total', value: money(meta.total), hint: `${meta.count} expense${meta.count === 1 ? '' : 's'}` },
    { label: 'Category limits', value: money(meta.budget?.limit) },
    { label: 'Spent', value: money(meta.budget?.spent) },
    { label: 'Left', value: money(meta.budget?.left), tone: Number(meta.budget?.left) < 0 ? 'text-negative' : '' },
  ]),
  after: async (box) => yearlyChartCard(box, { model: 'expenses', label: 'Expenses', color: 'c-expenses', years: (await loadOptions()).years }),
});
