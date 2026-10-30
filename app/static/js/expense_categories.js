// The expense categories page. Markup: templates/expense_categories.html
import { $, api, bindList, formatDate, money, recordForm, toastError } from './common.js';
import { draw } from './chart.js';

const refresh = () => { list.reload(); loadChart(); };

const form = recordForm($('#record-dialog'), {
  path: '/expense_categories',
  noun: 'category',
  defaults: () => ({ name: '', limit: '0' }),
  fromRecord: (r) => ({ name: r.display_name, limit: r.limit }),
  toBody: (v) => ({ name: v.name, limit: v.limit === '' ? '0' : v.limit }),
  onSaved: refresh,
});

const list = bindList({
  path: '/expense_categories',
  form,
  noun: 'category',
  undo: 'It is hidden; its expenses stay.',
  onDeleted: refresh,
  open: (row) => { location.href = `/expense_categories/${row.id}`; }, // double click
  cells: (row) => ({
    name: row.display_name,
    added: formatDate(row.created_at),
    limit: Number(row.limit) > 0 ? money(row.limit) : { text: 'No limit', class: 'text-muted' },
  }),
});

async function loadChart() {
  try {
    const { data } = await api.get('/expense_categories/reports/monthly');
    draw($('[data-chart]'), { type: 'bar', labels: data.names, series: [{ label: 'Spent', data: data.totals, color: 'c-expenses' }] });
  } catch (error) {
    toastError(error);
  }
}

loadChart();
