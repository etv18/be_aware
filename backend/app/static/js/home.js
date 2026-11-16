// The home page. Markup: templates/home.html
import { $, $$, MONTHS, api, loadOptions, money, setStats, sum, titleCase, toNumber, toastError } from './common.js';
import { draw } from './chart.js';

$('[data-page-subtitle]').textContent = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

// ------------------------------------------------------------------ the figures and this month
async function loadTiles() {
  const d = (await api.get('/dashboard')).data;
  const incomes = toNumber(d.month.incomes);
  const expenses = toNumber(d.month.expenses);

  setStats({
    cash: money(d.cash_balance),
    banks: money(d.bank_total),
    cards: money(d.cards_used),
    collect: { text: money(d.to_collect), hint: `${d.active_loans} active loan${d.active_loans === 1 ? '' : 's'}` },
    pay: { text: money(d.to_pay), hint: `${d.active_debts} active debt${d.active_debts === 1 ? '' : 's'}` },
    left: money(incomes - expenses),
    'month-incomes': money(d.month.incomes),
    'month-expenses': money(d.month.expenses),
  });

  draw($('[data-month]'), {
    type: 'doughnut', labels: ['Incomes', 'Expenses'], legend: false,
    series: [{ label: 'This month', data: incomes + expenses === 0 ? [0, 0] : [incomes, expenses], color: ['c-incomes', 'c-expenses'] }],
  });
}

// ------------------------------------------------------------------ the year: chart, table and totals
const KIND_KEY = 'home-chart-kind';
let kind = 'bar';
try { kind = localStorage.getItem(KIND_KEY) === 'line' ? 'line' : 'bar'; } catch { /* private mode */ }
let flow = null;

function drawFlow() {
  $$('[data-kind]').forEach((button) => button.setAttribute('aria-selected', String(button.dataset.kind === kind)));
  if (!flow) return;
  draw($('[data-flow]'), {
    type: kind,
    series: [{ label: 'Incomes', data: flow.incomes, color: 'c-incomes' }, { label: 'Expenses', data: flow.expenses, color: 'c-expenses' }],
  });
}

$$('[data-kind]').forEach((button) => button.addEventListener('click', () => {
  kind = button.dataset.kind;
  try { localStorage.setItem(KIND_KEY, kind); } catch { /* private mode */ }
  drawFlow();
}));

const sign = (value) => (value < 0 ? 'text-negative' : value > 0 ? 'text-positive' : 'text-faint');

function cell(tag, text, className = '') {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

function row(label, incomes, expenses, strong) {
  const balance = incomes - expenses;
  const tr = document.createElement('tr');
  tr.append(
    cell('td', label, strong ? 'font-semibold' : 'font-medium'),
    cell('td', money(incomes), `num text-right ${strong ? 'font-semibold' : incomes ? '' : 'text-faint'}`),
    cell('td', money(expenses), `num text-right ${strong ? 'font-semibold' : expenses ? '' : 'text-faint'}`),
    cell('td', money(balance), `num text-right ${strong ? 'font-semibold' : 'font-medium'} ${sign(balance)}`),
  );
  return tr;
}

function drawMonths() {
  const incomes = flow.incomes.map(toNumber);
  const expenses = flow.expenses.map(toNumber);
  $('[data-months]').replaceChildren(
    ...MONTHS.map((month, i) => row(month, incomes[i], expenses[i], false)),
    row('Total', sum(incomes), sum(expenses), true),
  );
}

async function loadYear() {
  const year = $('[data-year]').value;
  const [cashFlow, all] = await Promise.all([api.get('/reports/cash_flow', { year }), api.get('/reports/yearly/all', { year })]);
  flow = cashFlow.data.report;
  $('[data-year-label]').textContent = `· ${year}`;
  drawFlow();
  drawMonths();

  $('[data-kinds]').replaceChildren(...Object.entries(all.data.report).map(([name, months]) => {
    const total = sum(months);
    const li = document.createElement('li');
    li.className = 'flex items-center justify-between px-4 py-2.5 text-sm';
    li.append(cell('span', titleCase(name)), cell('span', money(total), `num ${total ? 'font-medium' : 'text-faint'}`));
    return li;
  }));
}

async function main() {
  const { years } = await loadOptions();
  const thisYear = new Date().getFullYear();
  const select = $('[data-year]');
  select.replaceChildren(...years.map((y) => new Option(y, y)));
  select.value = String(thisYear);
  if (!select.value) select.selectedIndex = 0;
  select.addEventListener('change', () => loadYear().catch(toastError));
  await Promise.all([loadTiles(), loadYear()]);
}

main().catch(toastError);
