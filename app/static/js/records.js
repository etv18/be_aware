// The records of one bank account / card / category, one tab per kind of record (markup: partials/ui.html records_tabs).
// Each kind says which columns it shows. Cells are filled with textContent, so nothing a person typed can run as HTML.
import { $, bindFilters, filterRows, formatDate, money, source, sum } from './common.js';

const column = (label, text, options = {}) => ({ label, text, ...options });

const date = column('Date', (r) => formatDate(r.created_at), { class: 'whitespace-nowrap text-muted' });
const amount = (tone = '') => column('Amount', (r) => money(r.amount), { right: true, class: `font-medium ${tone}` });
const person = column('Person', (r) => r.person_name || '–', { sub: (r) => r.description });
const description = column('Description', (r) => r.description || '–');

// loans and debts share their columns; only the "where the money went" label changes
const obligation = (sourceLabel, isActiveStsLabel, isActiveStsClass) => [ //     status: row.is_active ?  : { text: 'Paid', class: 'tag-positive' },

  person,
  column('Status', (r) => (r.is_active ? isActiveStsLabel.toUpperCase() : 'Paid'), { class: (r) => (r.is_active ? isActiveStsClass : 'text-positive font-bold') }),
  column(sourceLabel, source),
  date,
  column('Paid', (r) => money(r.total_paid), { right: true }),
  column('Remaining', (r) => money(r.remaining_amount), { right: true }),
  amount(),
];

const resolve = (value, row) => (typeof value === 'function' ? value(row) : value); // util function for decompiling classes in {options} param from

const KINDS = {
  expenses: ['Expenses', [description, column('Category', (r) => r.expense_category_name || '–'), column('Paid with', source), date, amount('text-negative')]],
  incomes: ['Incomes', [description, column('Received in', source), date, amount('text-positive')]],
  deposits: ['Deposits', [description, column('Into account', (r) => r.bank_account_name || '–'), date, amount()]],
  withdrawals: ['Withdrawals', [description, column('From account', (r) => r.bank_account_name || '–'), date, amount()]],
  loans: ['Loans', obligation('Lent from', 'COLLECT', 'text-yellow-400 font-black')],
  loan_payments: ['Loan payments', [person, column('Received in', source), date, amount('text-positive')]],
  debts: ['Debts', obligation('Received in', 'ACTIVE', 'text-negative font-black')],
  debt_payments: ['Debt payments', [person, column('Paid from', source), date, amount('text-negative')]],
  credit_card_payments: ['Card payments', [column('Card', (r) => r.credit_card_name || '–'), column('Paid from', (r) => (r.is_cashback ? 'Cashback' : r.bank_account_name || '–')), date, amount('text-positive')]],
  bank_transfers: ['Transfers', [column('Code', (r) => r.code, { class: 'font-mono text-xs' }), column('From', (r) => r.from_bank_account_name || '–'), column('To', (r) => r.to_bank_account_name || '–'), date, amount()]],
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function buildTable(columns, rows) {
  const table = el('table', 'table');
  const head = el('tr');
  columns.forEach((c) => head.append(el('th', c.right ? 'text-right' : '', c.label)));
  const thead = el('thead');
  thead.append(head);
  table.append(thead);

  const body = el('tbody');
  rows.forEach((row) => {
    const tr = el('tr');
    columns.forEach((c) => {
     // const td = el('td', `${c.right ? 'num text-right' : ''} ${c.class || ''}`);
     const td = el('td', `${c.right ? 'num text-right' : ''} ${resolve(c.class, row) || ''}`);
      td.append(el('span', c.sub ? `block font-medium` : '', c.text(row)));
      const sub = c.sub?.(row);
      if (sub) td.append(el('span', `block max-w-[28ch] truncate text-xs text-muted`, sub));
      tr.append(td);
    });
    body.append(tr);
  });
  table.append(body);
  return table;
}

/** recordsTabs($('[data-records]'), records) where records = { expenses: [...], incomes: [...], ... } from the server. */
export function recordsTabs(root, records) {
  const kinds = Object.keys(KINDS).filter((kind) => records[kind]?.length);
  const tabs = $('[data-tabs]', root);
  const body = $('[data-records-body]', root);
  const emptyBox = $('[data-empty]', root);
  const totalBar = $('[data-total-bar]', root);

  if (!kinds.length) { // nothing at all: only the "No records yet" message
    $('.card', root).querySelectorAll('[data-filters], [data-records-body], [data-total-bar]').forEach((part) => part.classList.add('hidden'));
    emptyBox.classList.remove('hidden');
    tabs.closest('.scroll-x').classList.add('hidden');
    return;
  }

  let current = kinds[0];
  let filters = {};

  tabs.replaceChildren(...kinds.map((kind) => {
    const button = el('button', '', `${KINDS[kind][0]} `);
    button.type = 'button';
    button.setAttribute('role', 'tab');
    button.dataset.kind = kind;
    button.append(el('span', 'text-faint', String(records[kind].length)));
    button.addEventListener('click', () => { current = kind; draw(); });
    return button;
  }));

  function draw() {
    const rows = filterRows(records[current], filters);
    const filtering = Boolean(filters.q || (filters.start && filters.end));
    [...tabs.children].forEach((tab) => tab.setAttribute('aria-selected', String(tab.dataset.kind === current)));
    body.replaceChildren(buildTable(KINDS[current][1], rows));
    emptyBox.classList.toggle('hidden', rows.length > 0);
    $('[data-empty-title]', emptyBox).textContent = 'Nothing matches';
    $('[data-empty-text]', emptyBox).textContent = 'Try other words, another amount or another date range.';
    $('[data-total-label]', totalBar).textContent = `${filtering ? 'Filtered total' : 'Total'} · ${rows.length} ${rows.length === 1 ? 'record' : 'records'}`;
    $('[data-total-value]', totalBar).textContent = money(sum(rows, 'amount'));
  }

  bindFilters($('[data-filters]', root), (state) => { filters = state; draw(); });
  draw();
}
