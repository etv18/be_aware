// One credit card: its figures, a chart and everything that moved through it. Markup: templates/credit_card.html
import { $, api, money, setStats, toastError } from './common.js';
import { draw } from './chart.js';
import { recordsTabs } from './records.js';
import { cardPaymentForm } from './forms.js';

const id = $('#page').dataset.id;
const year = new Date().getFullYear();

async function main() {
  const { data: { credit_card: card, records } } = await api.get(`/credit_cards/${id}/records`);

  $('[data-page-title]').textContent = card.nick_name;
  $('[data-page-subtitle]').textContent = card.bank_name || '';
  $('[data-chart-title]').textContent = `Per month · ${year}`;
  setStats({ limit: money(card.limit), used: money(card.used), available: money(card.amount_available) });
  recordsTabs($('[data-records]'), records);

  const payment = cardPaymentForm({ onSaved: () => location.reload() });
  const button = $('[data-pay]');
  button.classList.toggle('hidden', !card.is_active); // only an active card can be paid
  button.addEventListener('click', () => payment.open(card));

  const { data: report } = await api.get(`/credit_cards/${id}/reports/yearly`, { year });
  const info = report.associations_info;
  draw($('[data-chart]'), {
    type: 'bar',
    series: [
      { label: 'Expenses', data: info.expenses, color: 'c-expenses' },
      { label: 'Payments', data: info.credit_card_payments, color: 'c-incomes' },
      { label: 'Loans', data: info.loans, color: 'c-loans' },
    ],
  });
}

main().catch(toastError);
