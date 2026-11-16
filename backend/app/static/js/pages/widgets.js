// Pieces several pages share: the page header, stat cards, the search bar and the yearly chart.
import { html } from '../core/html.js';
import { getData } from '../core/api.js';
import { draw } from '../core/chart.js';
import { currentYear, MONTHS, money, toNumber } from '../core/format.js';
import { icon, toastError } from '../core/ui.js';
import { clearDate, enhanceDates } from '../core/datepicker.js';

export const pageHeader = ({ title, subtitle = '', back = null, actions = '' }) => html`
  <header class="mb-6 flex flex-wrap items-end justify-between gap-3">
    <div class="min-w-0">
      ${back ? html`<a href="${back.href}" class="mb-2 inline-flex items-center gap-1 text-sm text-muted hover:text-ink">${icon('chevron-left')}${back.label}</a>` : ''}
      <h1 class="truncate text-xl font-semibold">${title}</h1>
      ${subtitle ? html`<p class="mt-0.5 text-sm text-muted">${subtitle}</p>` : ''}
    </div>
    <div class="flex flex-wrap items-center gap-2" data-header-actions>${actions}</div>
  </header>`;

export const button = (label, { name, glyph = '', kind = 'outline', href = '' } = {}) => (href
  ? html`<a href="${href}" class="btn btn-${kind}">${glyph ? icon(glyph) : ''}${label}</a>`
  : html`<button type="button" class="btn btn-${kind}" data-do="${name}">${glyph ? icon(glyph) : ''}${label}</button>`);

/** [{label, value, hint?, tone?}] as a row of figures. */
export const statCards = (items) => html`
  <div class="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-${Math.min(items.length, 4)}">
    ${items.map((item) => html`
      <div class="card px-4 py-3.5">
        <p class="text-xs text-muted">${item.label}</p>
        <p class="num mt-1 truncate text-xl font-semibold ${item.tone || ''}">${item.value}</p>
        ${item.hint ? html`<p class="mt-0.5 truncate text-xs text-muted">${item.hint}</p>` : ''}
      </div>`)}
  </div>`;

/** Search box and date range for a list. Wire it with bindFilters(). */
export const filterBar = (placeholder = 'Search…') => html`
  <div class="flex flex-col gap-2 border-b border-line p-3 sm:flex-row sm:items-center">
    <div class="relative flex-1">
      <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-faint">${icon('search')}</span>
      <input class="input pl-9" type="search" placeholder="${placeholder}" data-filter="q" aria-label="Search">
    </div>
    <div class="flex items-center gap-2">
      <input class="input w-full sm:w-40" type="text" data-picker="date" placeholder="From" data-filter="start" aria-label="From date">
      <span class="text-faint">–</span>
      <input class="input w-full sm:w-40" type="text" data-picker="date" placeholder="To" data-filter="end" aria-label="To date">
      <button type="button" class="btn-icon shrink-0" data-filter-clear title="Clear filters" aria-label="Clear filters">${icon('filter-x')}</button>
    </div>
  </div>`;

/** The line under a table: how many records and what they add up to. */
export const totalBar = () => html`
  <div class="flex items-center justify-between gap-3 border-t border-line bg-sunken/40 px-4 py-2.5 text-sm" data-total-bar>
    <span class="text-muted" data-total-label>Total</span>
    <span class="num font-semibold" data-total-value></span>
  </div>`;

export function showTotal(container, rows, filtering, total) {
  const bar = container.querySelector('[data-total-bar]');
  if (!bar) return;
  bar.querySelector('[data-total-label]').textContent = `${filtering ? 'Filtered total' : 'Total'} · ${rows.length} ${rows.length === 1 ? 'record' : 'records'}`;
  bar.querySelector('[data-total-value]').textContent = money(total);
}

export function bindFilters(root, onChange) {
  enhanceDates(root);
  const inputs = [...root.querySelectorAll('[data-filter]')];
  const state = () => Object.fromEntries(inputs.map((i) => [i.dataset.filter, i.value || null]));

  let timer;
  const changed = (event) => {
    const { start, end } = state();
    if (event.target.dataset.picker && Boolean(start) !== Boolean(end)) return; // wait for both dates
    clearTimeout(timer);
    timer = setTimeout(() => onChange(state()), event.target.type === 'search' ? 280 : 0);
  };
  inputs.forEach((input) => input.addEventListener('input', changed));
  root.querySelector('[data-filter-clear]')?.addEventListener('click', () => {
    inputs.forEach(clearDate);
    onChange(state());
  });
  return state;
}

/** A card with a year picker and a chart of one kind of record per month. */
export function yearlyChartCard(container, { model, label, color, years, type = 'line' }) {
  const year = currentYear();
  container.innerHTML = html`
    <div class="card card-pad">
      <div class="mb-4 flex items-center justify-between gap-3">
        <h2 class="text-sm font-semibold">${label} per month</h2>
        <select class="select h-8 w-24 text-xs" data-year aria-label="Year">
          ${(years || [year]).map((y) => html`<option value="${y}" ${y === year ? 'selected' : ''}>${y}</option>`)}
        </select>
      </div>
      <div class="relative h-64"><canvas></canvas></div>
      <p class="num mt-3 text-sm text-muted">Total <span class="font-medium text-ink" data-total></span></p>
    </div>`.toString();

  const canvas = container.querySelector('canvas');
  const select = container.querySelector('[data-year]');
  const total = container.querySelector('[data-total]');

  async function load() {
    try {
      const report = await getData('/stats/yearly', { model, year: select.value });
      const data = Object.entries(report).find(([key]) => Array.isArray(report[key]) && key !== 'months')?.[1] || [];
      total.textContent = money(data.reduce((sum, v) => sum + toNumber(v), 0));
      draw(canvas, { type, labels: MONTHS, series: [{ label, data, color }] });
    } catch (error) {
      toastError(error);
    }
  }
  select.addEventListener('change', load);
  return load();
}
