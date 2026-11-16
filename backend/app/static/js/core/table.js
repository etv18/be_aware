// Tables that turn into cards on a phone. Both views come from the same column list:
//   column: { label, render(row) -> text | Safe, align?: 'right', primary?: true, amount?: true, hideOnMobile?: true }
// `primary` is the card title, `amount` sits opposite it, the rest become "label  value" lines.
import { html } from './html.js';
import { icon, emptyState } from './ui.js';

function actionButtons(actions, row) {
  return actions
    .filter((a) => !a.show || a.show(row))
    .map((a) => html`<button type="button" class="btn-icon ${a.danger ? 'btn-icon-danger' : ''}" data-action="${a.name}" data-id="${row.id}" title="${a.label}" aria-label="${a.label}">${icon(a.icon)}</button>`);
}

export function renderTable({ columns, rows, actions = [], empty, rowLink }) {
  if (!rows.length) return empty || emptyState('Nothing here yet');

  const primary = columns.find((c) => c.primary) || columns[0];
  const amount = columns.find((c) => c.amount);
  const rest = columns.filter((c) => c !== primary && c !== amount && !c.hideOnMobile);

  const table = html`
    <div class="table-wrap table-scroll hidden md:block">
      <table class="table">
        <thead><tr>
          ${columns.map((c) => html`<th class="${c.align === 'right' ? 'text-right' : ''}">${c.label}</th>`)}
          ${actions.length ? html`<th class="w-px"><span class="sr-only">Actions</span></th>` : ''}
        </tr></thead>
        <tbody>
          ${rows.map((row) => html`<tr data-row="${row.id}">
            ${columns.map((c) => html`<td class="${c.align === 'right' ? 'num text-right' : ''} ${c.className || ''}">${c.render(row)}</td>`)}
            ${actions.length ? html`<td><div class="flex justify-end gap-0.5">${actionButtons(actions, row)}</div></td>` : ''}
          </tr>`)}
        </tbody>
      </table>
    </div>`;

  const cards = html`
    <ul class="cards-scroll divide-y divide-line md:hidden">
      ${rows.map((row) => html`<li class="px-4 py-3" data-row="${row.id}">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 font-medium">${primary.render(row)}</div>
          ${amount ? html`<div class="num shrink-0 font-medium">${amount.render(row)}</div>` : ''}
        </div>
        <dl class="mt-1.5 space-y-0.5 text-xs text-muted">
          ${rest.map((c) => html`<div class="flex justify-between gap-3"><dt>${c.label}</dt><dd class="min-w-0 truncate text-right text-ink">${c.render(row)}</dd></div>`)}
        </dl>
        ${actions.length ? html`<div class="mt-2 flex justify-end gap-0.5">${actionButtons(actions, row)}</div>` : ''}
      </li>`)}
    </ul>`;

  return html`${table}${cards}`;
}

/** Route clicks on the row buttons to handlers: { edit: (row) => ..., delete: (row) => ... } */
export function bindActions(container, getRows, handlers) {
  container.addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (!button || !container.contains(button)) return;
    const handler = handlers[button.dataset.action];
    if (!handler) return;
    const row = getRows().find((r) => String(r.id) === button.dataset.id);
    if (row) handler(row, button);
  });
}
