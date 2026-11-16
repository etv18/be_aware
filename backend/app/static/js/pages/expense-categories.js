import { getData } from '../core/api.js';
import { html } from '../core/html.js';
import { draw } from '../core/chart.js';
import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';

listPage({
  resource: 'expense-categories',
  title: 'Expense categories',
  subtitle: 'Group your expenses and give each group a monthly limit.',
  columns: columns.expenseCategories,
  newLabel: 'New category',
  noFilters: true,
  handlers: { open: (row) => { location.href = `/expense_categories/associated_records/${row.id}`; } },
  after: async (box, { }) => {
    box.innerHTML = html`<div class="card card-pad"><h2 class="mb-4 text-sm font-semibold">Spent this month, by category</h2><div class="relative h-64"><canvas></canvas></div></div>`.toString();
    const report = await getData('/expense_categories/reports/monthly');
    draw(box.querySelector('canvas'), { type: 'bar', labels: report.names, series: [{ label: 'Spent', data: report.totals, color: 'c-expenses' }] });
  },
});
