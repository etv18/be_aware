// Records of one bank account / card / category, one tab per kind of record,
// with a search (description or amount), a date range and the total of what is shown.
import { filterRows, totalOf } from '../core/filtering.js';
import { html, mount } from '../core/html.js';
import { renderTable } from '../core/table.js';
import { emptyState } from '../core/ui.js';
import * as columns from '../domain/columns.js';
import { bindFilters, filterBar, showTotal, totalBar } from './widgets.js';

const KINDS = {
  expenses: ['Expenses', columns.expenses],
  incomes: ['Incomes', columns.incomes],
  deposits: ['Deposits', columns.deposits],
  withdrawals: ['Withdrawals', columns.withdrawals],
  loans: ['Loans', columns.loans],
  loan_payments: ['Loan payments', columns.loanPayments],
  debts: ['Debts', columns.debts],
  debt_payments: ['Debt payments', columns.debtPayments],
  credit_card_payments: ['Card payments', columns.creditCardPayments],
  bank_transfers: ['Transfers', columns.bankTransfers],
};

export function recordsTabs(container, records) {
  const kinds = Object.keys(KINDS).filter((kind) => records[kind]?.length);
  if (!kinds.length) {
    mount(container, html`<div class="card">${emptyState('No records yet', 'Everything that moves through here will be listed.')}</div>`);
    return;
  }

  let current = kinds[0];
  let filters = {};

  mount(container, html`
    <div class="mb-3 scroll-x"><div class="tabs" role="tablist">
      ${kinds.map((kind) => html`<button type="button" role="tab" data-kind="${kind}">${KINDS[kind][0]} <span class="text-faint">${records[kind].length}</span></button>`)}
    </div></div>
    <section class="card overflow-hidden">
      ${filterBar('Search description or amount…')}
      <div data-body></div>
      ${totalBar()}
    </section>`);

  const body = container.querySelector('[data-body]');
  const tabs = [...container.querySelectorAll('[data-kind]')];

  const draw = () => {
    const rows = filterRows(records[current], filters);
    const filtering = Boolean(filters.q || (filters.start && filters.end));
    tabs.forEach((tab) => tab.setAttribute('aria-selected', String(tab.dataset.kind === current)));
    body.innerHTML = renderTable({
      columns: KINDS[current][1],
      rows,
      empty: emptyState('Nothing matches', 'Try other words, another amount or another date range.'),
    }).toString();
    showTotal(container, rows, filtering, totalOf(rows));
  };

  tabs.forEach((tab) => tab.addEventListener('click', () => { current = tab.dataset.kind; draw(); }));
  bindFilters(container, (state) => { filters = Object.fromEntries(Object.entries(state).filter(([, v]) => v)); draw(); });
  draw();
}
