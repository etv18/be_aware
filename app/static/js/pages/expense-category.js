import { getData } from '../core/api.js';
import { money } from '../core/format.js';
import { html, mount } from '../core/html.js';
import { recordsTabs } from './records-tabs.js';
import { pageHeader, statCards } from './widgets.js';

const app = document.getElementById('app');
const { expense_category: category, records } = await getData(`/expense_categories/${app.dataset.id}/records`);
const spent = (records.expenses || []).reduce((sum, e) => sum + Number(e.amount), 0);

mount(app, html`
  ${pageHeader({ title: category.display_name, back: { href: '/expense_categories/index', label: 'Expense categories' } })}
  ${statCards([
    { label: 'Monthly limit', value: Number(category.limit) > 0 ? money(category.limit) : 'No limit' },
    { label: 'Spent so far', value: money(spent), hint: `${(records.expenses || []).length} expenses` },
  ])}
  <div data-records></div>`);
recordsTabs(app.querySelector('[data-records]'), records);
