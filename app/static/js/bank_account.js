// One bank account: its figures, a chart and everything that moved through it. Markup: templates/bank_account.html
import { $, api, money, setStats, toastError } from './common.js';
import { draw } from './chart.js';
import { recordsTabs } from './records.js';
import { transferForm } from './forms.js';

const id = $('#page').dataset.id;
const year = new Date().getFullYear();

async function main() {
  const { data: { bank_account: account, records } } = await api.get(`/bank_accounts/${id}/records`);

  $('[data-page-title]').textContent = account.nick_name;
  $('[data-page-subtitle]').textContent = [account.bank_name, account.account_number].filter(Boolean).join(' · ');
  $('[data-chart-title]').textContent = `Money in and out, per month · ${year}`;
  setStats({ balance: money(account.amount_available), status: account.is_active ? 'Active' : 'Inactive' });
  recordsTabs($('[data-records]'), records);

  const transfer = transferForm({ onSaved: () => location.reload() });
  const button = $('[data-transfer]');
  button.classList.toggle('hidden', !account.is_active); // only an active account can send money
  button.addEventListener('click', () => transfer.open(account));

  const { data: flow } = await api.get(`/bank_accounts/${id}/reports/cash_flow`, { year });
  draw($('[data-chart]'), {
    type: 'bar',
    series: [{ label: 'In', data: flow.incomings, color: 'c-incomes' }, { label: 'Out', data: flow.outgoings, color: 'c-expenses' }],
  });
}

main().catch(toastError);
