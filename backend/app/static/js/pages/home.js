import { getData, loadOptions } from '../core/api.js';
import { draw } from '../core/chart.js';
import { currentYear, MONTHS, money, titleCase, toNumber } from '../core/format.js';
import { html, mount } from '../core/html.js';
import { icon, toastError } from '../core/ui.js';
import { pageHeader } from './widgets.js';

const app = document.getElementById('app');

const tile = (glyph, label, value, href, hint = '') => html`
  <a href="${href}" class="card flex items-start gap-3 p-4 transition-colors hover:bg-sunken">
    <span class="flex size-9 shrink-0 items-center justify-center rounded-lg bg-sunken text-muted">${icon(glyph)}</span>
    <span class="min-w-0"><span class="block text-xs text-muted">${label}</span><span class="num block truncate text-lg font-semibold">${value}</span>${hint ? html`<span class="block truncate text-xs text-muted">${hint}</span>` : ''}</span>
  </a>`;

mount(app, html`
  ${pageHeader({ title: 'Home', subtitle: new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) })}
  <div data-tiles class="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3"></div>
  <div class="mb-6 grid gap-4 lg:grid-cols-3">
    <section class="card card-pad lg:col-span-2">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-sm font-semibold">Incomes and expenses</h2>
        <div class="flex items-center gap-2">
          <div class="tabs" role="tablist" aria-label="Chart type">
            <button type="button" role="tab" data-kind="bar" aria-selected="true">${icon('chart-column')}Bars</button>
            <button type="button" role="tab" data-kind="line" aria-selected="false">${icon('chart-line')}Lines</button>
          </div>
          <select class="select h-8 w-24 text-xs" data-year aria-label="Year"></select>
        </div>
      </div>
      <div class="relative h-64"><canvas data-flow></canvas></div>
    </section>
    <section class="card card-pad">
      <h2 class="mb-4 text-sm font-semibold">This month</h2>
      <div class="relative mx-auto h-48 max-w-[14rem]"><canvas data-month></canvas></div>
      <dl class="num mt-4 space-y-1.5 text-sm" data-month-figures></dl>
    </section>
  </div>
  <section class="card mb-6 overflow-hidden">
    <h2 class="border-b border-line px-4 py-3 text-sm font-semibold">Month by month <span class="font-normal text-muted" data-year-label></span></h2>
    <div data-summary></div>
  </section>
  <section class="card overflow-hidden">
    <h2 class="border-b border-line px-4 py-3 text-sm font-semibold">Year by kind of record</h2>
    <div data-kinds></div>
  </section>`);

const tiles = app.querySelector('[data-tiles]');
const select = app.querySelector('[data-year]');

async function loadTiles() {
  const d = await getData('/dashboard');
  mount(tiles, html`
    ${tile('coins', 'Cash on hand', money(d.cash_balance), '/cashledger/index')}
    ${tile('wallet', 'In bank accounts', money(d.bank_total), '/bank_accounts/index')}
    ${tile('credit-card', 'Used on cards', money(d.cards_used), '/credit_cards/index')}
    ${tile('hand-coins', 'To collect', money(d.to_collect), '/loans/index', `${d.active_loans} active loan${d.active_loans === 1 ? '' : 's'}`)}
    ${tile('scroll-text', 'To pay', money(d.to_pay), '/debts/index', `${d.active_debts} active debt${d.active_debts === 1 ? '' : 's'}`)}
    ${tile('trending-up', 'Left this month', money(toNumber(d.month.incomes) - toNumber(d.month.expenses)), '/expenses/index')}`);

  const incomes = toNumber(d.month.incomes);
  const expenses = toNumber(d.month.expenses);
  draw(app.querySelector('[data-month]'), {
    type: 'doughnut', labels: ['Incomes', 'Expenses'], legend: false,
    series: [{ label: 'This month', data: incomes + expenses === 0 ? [0, 0] : [incomes, expenses], color: ['c-incomes', 'c-expenses'] }],
  });
  mount(app.querySelector('[data-month-figures]'), html`
    <div class="flex justify-between"><dt class="flex items-center gap-2"><span class="dot" style="background: rgb(var(--c-incomes))"></span>Incomes</dt><dd>${money(d.month.incomes)}</dd></div>
    <div class="flex justify-between"><dt class="flex items-center gap-2"><span class="dot" style="background: rgb(var(--c-expenses))"></span>Expenses</dt><dd>${money(d.month.expenses)}</dd></div>`);
}

const KIND_KEY = 'home-chart-kind';
let kind = 'bar';
try { kind = localStorage.getItem(KIND_KEY) === 'line' ? 'line' : 'bar'; } catch { /* private mode */ }
let flow = null;

const sign = (value) => (value < 0 ? 'text-negative' : value > 0 ? 'text-positive' : 'text-faint');

function drawFlow() {
  app.querySelectorAll('[data-kind]').forEach((button) => button.setAttribute('aria-selected', String(button.dataset.kind === kind)));
  if (!flow) return;
  draw(app.querySelector('[data-flow]'), {
    type: kind, labels: MONTHS,
    series: [{ label: 'Incomes', data: flow.incomes, color: 'c-incomes' }, { label: 'Expenses', data: flow.expenses, color: 'c-expenses' }],
  });
}

app.querySelectorAll('[data-kind]').forEach((button) => button.addEventListener('click', () => {
  kind = button.dataset.kind;
  try { localStorage.setItem(KIND_KEY, kind); } catch { /* private mode */ }
  drawFlow();
}));

/** Incomes, expenses and balance of every month: months across on wide screens, down the page on a phone. */
function drawSummary() {
  const incomes = flow.incomes.map(toNumber);
  const expenses = flow.expenses.map(toNumber);
  const balances = incomes.map((value, i) => value - expenses[i]);
  const total = (list) => list.reduce((sum, value) => sum + value, 0);
  const cell = (value, extra = '') => html`<td class="num right ${extra}">${money(value)}</td>`;

  mount(app.querySelector('[data-summary]'), html`
    <div class="table-wrap hidden md:block">
      <table class="table">
        <thead><tr><th>Month</th>${MONTHS.map((m) => html`<th class="right">${m}</th>`)}<th class="right">Total</th></tr></thead>
        <tbody>
          <tr><th class="text-ink">Incomes</th>${incomes.map((v) => cell(v, v ? '' : 'text-faint'))}${cell(total(incomes), 'font-semibold')}</tr>
          <tr><th class="text-ink">Expenses</th>${expenses.map((v) => cell(v, v ? '' : 'text-faint'))}${cell(total(expenses), 'font-semibold')}</tr>
          <tr><th class="text-ink">Balance</th>${balances.map((v) => cell(v, `font-medium ${sign(v)}`))}${cell(total(balances), `font-semibold ${sign(total(balances))}`)}</tr>
        </tbody>
      </table>
    </div>
    <div class="table-wrap md:hidden">
      <table class="table [&_td]:!px-2.5 [&_th]:!px-2.5 text-[13px]">
        <thead><tr><th>Month</th><th class="right">Incomes</th><th class="right">Expenses</th><th class="right">Balance</th></tr></thead>
        <tbody>
          ${MONTHS.map((m, i) => html`<tr><td class="font-medium">${m}</td>${cell(incomes[i], incomes[i] ? '' : 'text-faint')}${cell(expenses[i], expenses[i] ? '' : 'text-faint')}${cell(balances[i], `font-medium ${sign(balances[i])}`)}</tr>`)}
          <tr><td class="font-semibold">Total</td>${cell(total(incomes), 'font-semibold')}${cell(total(expenses), 'font-semibold')}${cell(total(balances), `font-semibold ${sign(total(balances))}`)}</tr>
        </tbody>
      </table>
    </div>`);
}

async function loadYear() {
  const year = select.value;
  const [cashFlow, all] = await Promise.all([getData('/stats/cash-flow', { year }), getData('/stats/yearly/all', { year })]);
  flow = cashFlow.report;
  app.querySelector('[data-year-label]').textContent = `· ${year}`;
  drawFlow();
  drawSummary();
  const rows = Object.entries(all.report).map(([kind, months]) => [titleCase(kind), months.reduce((s, v) => s + toNumber(v), 0)]);
  mount(app.querySelector('[data-kinds]'), html`
    <ul class="divide-y divide-line">
      ${rows.map(([kind, total]) => html`<li class="flex items-center justify-between px-4 py-2.5 text-sm"><span>${kind}</span><span class="num ${total ? 'font-medium' : 'text-faint'}">${money(total)}</span></li>`)}
    </ul>`);
}

const { years } = await loadOptions();
select.innerHTML = years.map((y) => `<option value="${y}" ${y === currentYear() ? 'selected' : ''}>${y}</option>`).join('');
select.addEventListener('change', () => loadYear().catch(toastError));
await Promise.all([loadTiles(), loadYear()]).catch(toastError);
