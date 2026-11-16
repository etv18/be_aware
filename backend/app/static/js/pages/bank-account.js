import { getData } from '../core/api.js';
import { draw } from '../core/chart.js';
import { currentYear, MONTHS, money } from '../core/format.js';
import { html, mount } from '../core/html.js';
import { toastError } from '../core/ui.js';
import { manager } from '../domain/resources.js';
import { recordsTabs } from './records-tabs.js';
import { button, pageHeader, statCards } from './widgets.js';

const app = document.getElementById('app');
const id = app.dataset.id;

const { bank_account: account, records } = await getData(`/bank_accounts/${id}/records`);

mount(app, html`
  ${pageHeader({
    title: account.nick_name,
    subtitle: [account.bank_name, account.account_number].filter(Boolean).join(' · '),
    back: { href: '/bank_accounts/index', label: 'Bank accounts' },
    actions: account.is_active ? button('Transfer', { name: 'transfer', glyph: 'arrow-left-right', kind: 'primary' }) : '',
  })}
  ${statCards([{ label: 'Balance', value: money(account.amount_available) }, { label: 'Status', value: account.is_active ? 'Active' : 'Inactive' }])}
  <div class="card card-pad mb-6">
    <div class="mb-4 flex items-center justify-between gap-3">
      <h2 class="text-sm font-semibold">Money in and out, per month</h2>
      <span class="text-xs text-muted">${currentYear()}</span>
    </div>
    <div class="relative h-64"><canvas></canvas></div>
  </div>
  <div data-records></div>`);

recordsTabs(app.querySelector('[data-records]'), records);
app.querySelector('[data-do="transfer"]')?.addEventListener('click', () => {
  manager('bank-transfers', { onChange: () => location.reload(), ctx: { fromId: account.id, fromName: account.nick_name } }).create();
});

try {
  const flow = await getData(`/bank_accounts/${id}/reports/cash-flow`, { year: currentYear() });
  draw(app.querySelector('canvas'), {
    type: 'bar', labels: MONTHS,
    series: [{ label: 'In', data: flow.incomings, color: 'c-incomes' }, { label: 'Out', data: flow.outgoings, color: 'c-expenses' }],
  });
} catch (error) { toastError(error); }
