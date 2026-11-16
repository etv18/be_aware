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

const { credit_card: card, records } = await getData(`/credit_cards/${id}/records`);

mount(app, html`
  ${pageHeader({
    title: card.nick_name,
    subtitle: card.bank_name || '',
    back: { href: '/credit_cards/index', label: 'Credit cards' },
    actions: card.is_active ? button('Pay the card', { name: 'pay', glyph: 'banknote', kind: 'primary' }) : '',
  })}
  ${statCards([
    { label: 'Limit', value: money(card.limit) },
    { label: 'Used', value: money(card.used) },
    { label: 'Available', value: money(card.amount_available) },
  ])}
  <div class="card card-pad mb-6">
    <h2 class="mb-4 text-sm font-semibold">Per month · ${currentYear()}</h2>
    <div class="relative h-64"><canvas></canvas></div>
  </div>
  <div data-records></div>`);

recordsTabs(app.querySelector('[data-records]'), records);
app.querySelector('[data-do="pay"]')?.addEventListener('click', () => {
  manager('credit-card-payments', { onChange: () => location.reload(), ctx: { cardId: card.id } }).create();
});

try {
  const report = await getData(`/credit_cards/${id}/reports/yearly`, { year: currentYear() });
  const info = report.associations_info;
  draw(app.querySelector('canvas'), {
    type: 'bar', labels: MONTHS,
    series: [
      { label: 'Expenses', data: info.expenses, color: 'c-expenses' },
      { label: 'Payments', data: info.credit_card_payments, color: 'c-incomes' },
      { label: 'Loans', data: info.loans, color: 'c-loans' },
    ],
  });
} catch (error) { toastError(error); }
