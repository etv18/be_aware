// The page every "list of records" screen is made from: header, figures, search and dates, table, charts.
// A screen is just a description (see expenses.js); this file does the work.
import { api } from '../core/api.js';
import { html, mount } from '../core/html.js';
import { bindActions, renderTable } from '../core/table.js';
import { emptyState, icon, loadingRows, toastError } from '../core/ui.js';
import { manager, RESOURCES } from '../domain/resources.js';
import { filterRows, totalOf } from '../core/filtering.js';
import { bindFilters, button, filterBar, pageHeader, showTotal, totalBar } from './widgets.js';

const EDIT = { name: 'edit', icon: 'pencil', label: 'Edit' };
const DELETE = { name: 'delete', icon: 'trash-2', label: 'Delete', danger: true };

/**
 * listPage({
 *   resource: 'expenses',                 key of domain/resources.js (its path is also the list endpoint)
 *   listPath?: '/cashledger',           when the list is read from somewhere else
 *   title, subtitle, columns, newLabel, placeholder,
 *   note?: 'Showing this month.',        shown while no filter is active
 *   summary?: (meta, rows) => statCards(...)
 *   actions?: [...]                       extra row actions, in front of edit / delete (each has a handler)
 *   handlers?: { name: (row, ctx) => ... }
 *   readOnly?: true                       no new / edit / delete
 *   headerActions?: [button(...)]         extra buttons next to "New", wired in `handlers` by name
 *   after?: (container, ctx) => void      what goes below the table (charts)
 *   ctx?: {...}                           handed to the form definition
 *   localFilter?: true                    the list is filtered here instead of asking the server (small lists that belong to one record)
 *   total?: true                          a line under the table with the sum of the amounts shown
 * })
 */
export async function listPage(config) {
  const app = config.root || document.getElementById('app');
  const resource = RESOURCES[config.resource];
  const listPath = config.listPath || resource?.path;

  const actions = config.readOnly ? (config.actions || []) : [...(config.actions || []), EDIT, DELETE];

  mount(app, html`
    ${pageHeader({
      title: config.title,
      subtitle: config.subtitle,
      actions: html`${config.headerActions || ''}${!config.readOnly || config.canCreate ? button(config.newLabel || 'New', { name: 'new', glyph: 'plus', kind: 'primary' }) : ''}`,
    })}
    <div data-summary></div>
    <section class="card overflow-hidden">
      ${config.noFilters ? '' : filterBar(config.placeholder)}
      <div data-table>${loadingRows()}</div>
      ${config.total ? totalBar() : ''}
      ${config.note ? html`<p class="hidden border-t border-line px-4 py-2.5 text-xs text-muted" data-note>${config.note}</p>` : ''}
    </section>
    <div class="mt-6" data-after></div>`);

  const tableBox = app.querySelector('[data-table]');
  const summaryBox = app.querySelector('[data-summary]');
  const noteBox = app.querySelector('[data-note]');

  let rows = [];
  let filters = {};
  let sequence = 0;

  async function load() {
    const mine = ++sequence;
    try {
      const { data, meta } = await api.get(listPath, config.localFilter ? {} : filters);
      if (mine !== sequence) return; // a newer search is on its way
      rows = config.localFilter ? filterRows(data, filters) : data;
      const filtering = Boolean(filters.q || (filters.start && filters.end));

      if (config.summary) mount(summaryBox, config.summary(meta, rows, { filtering }));
      noteBox?.classList.toggle('hidden', filtering);
      if (config.total) showTotal(app, rows, filtering, totalOf(rows));

      tableBox.innerHTML = renderTable({
        columns: config.columns,
        rows,
        actions,
        empty: filtering
          ? emptyState('Nothing matches', 'Try other words or another date range.')
          : emptyState(config.emptyTitle || 'Nothing here yet', config.emptyText || (config.readOnly ? '' : `Use “${config.newLabel || 'New'}” to add the first one.`)),
      }).toString();
    } catch (error) {
      tableBox.innerHTML = html`<div class="p-8 text-center text-sm"><p class="text-negative">${error.message}</p><button class="btn btn-outline mt-3" data-retry>${icon('refresh-cw')}Try again</button></div>`.toString();
      tableBox.querySelector('[data-retry]').addEventListener('click', load);
      toastError(error);
    }
    config.onLoad?.({ rows, reload: load });
  }

  const records = resource ? manager(config.resource, { onChange: () => { load(); config.afterChange?.(); }, ctx: config.ctx }) : null;
  const context = { reload: load, rows: () => rows, records };

  const doHandlers = {
    new: () => records.create(),
    ...Object.fromEntries(Object.entries(config.handlers || {}).map(([name, fn]) => [name, () => fn(context)])),
  };
  app.querySelectorAll('[data-do]').forEach((el) => el.addEventListener('click', () => doHandlers[el.dataset.do]?.()));

  bindActions(tableBox, () => rows, {
    ...(records ? { edit: records.edit, delete: records.remove } : {}),
    ...Object.fromEntries(Object.entries(config.handlers || {}).map(([name, fn]) => [name, (row) => fn(row, context)])),
  });

  // a double click on a row runs the "open" handler (the page of that record's associated transactions)
  if (config.handlers?.open) {
    tableBox.classList.add('row-open');
    tableBox.addEventListener('dblclick', (event) => {
      if (event.target.closest('button, a, input, select')) return;
      const row = rows.find((r) => String(r.id) === event.target.closest('[data-row]')?.dataset.row);
      if (!row) return;
      window.getSelection()?.removeAllRanges();
      config.handlers.open(row, context);
    });
  }

  bindFilters(app, (state) => { filters = Object.fromEntries(Object.entries(state).filter(([, v]) => v)); load(); });

  await load();
  config.after?.(app.querySelector('[data-after]'), context);
  return context;
}
