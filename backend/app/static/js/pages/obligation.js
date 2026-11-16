// Loans and debts: the list pages and the page of one loan / debt with its payments.
import { getData } from '../core/api.js';
import { html, mount } from '../core/html.js';
import { money } from '../core/format.js';
import * as columns from '../domain/columns.js';
import { manager } from '../domain/resources.js';
import { listPage } from './list-page.js';
import { button, pageHeader, statCards, yearlyChartCard } from './widgets.js';
import { loadOptions } from '../core/api.js';

const KINDS = {
  loans: {
    noun: 'loan', plural: 'Loans', subtitle: 'Money you lent. Payments you receive reduce what is left.',
    columns: columns.loans, paymentsKey: 'loan-payments', parentKey: 'loan_id', base: '/loans/associated_records',
    paymentColumns: columns.loanPayments, model: 'loans', color: 'c-loans', owed: 'Still to collect', payLabel: 'Receive a payment',
  },
  debts: {
    noun: 'debt', plural: 'Debts', subtitle: 'Money you owe. Payments you make reduce what is left.',
    columns: columns.debts, paymentsKey: 'debt-payments', parentKey: 'debt_id', base: '/debts/associated/records',
    paymentColumns: columns.debtPayments, model: 'debts', color: 'c-debts', owed: 'Still to pay', payLabel: 'Make a payment',
  },
};

export function obligationList(kind) {
  const k = KINDS[kind];
  return listPage({
    resource: kind,
    title: k.plural,
    subtitle: k.subtitle,
    columns: k.columns,
    newLabel: `New ${k.noun}`,
    placeholder: `Search person, description, account…`,
    headerActions: button('All payments', { href: kind === 'loans' ? '/loan_payments/index' : '/debt_payments/index', glyph: 'list' }),
    actions: [{ name: 'pay', icon: 'hand-coins', label: k.payLabel, show: (r) => r.is_active }],
    handlers: {
      open: (row) => { location.href = `${k.base}/${row.id}`; }, // double click
      // one payment, in cash or into / out of a bank account
      pay: (row, { reload }) => manager(k.paymentsKey, { onChange: reload, ctx: { parentKey: k.parentKey, parentId: row.id } }).create(),
    },
    summary: (meta) => statCards([
      { label: k.owed, value: money(meta.remaining) },
      { label: 'Active', value: meta.actives ?? meta.active ?? 0 },
      { label: 'Paid', value: meta.paids ?? meta.paid ?? 0 },
    ]),
    after: async (box) => yearlyChartCard(box, { model: k.model, label: k.plural, color: k.color, years: (await loadOptions()).years }),
  });
}

export async function obligationDetail(kind) {
  const k = KINDS[kind];
  const app = document.getElementById('app');
  const id = app.dataset.id;
  const record = await getData(`/${kind}/${id}`);

  const figures = (row) => statCards([
    { label: 'Amount', value: money(row.amount) },
    { label: 'Paid', value: money(row.total_paid) },
    { label: 'Remaining', value: money(row.remaining_amount), tone: row.is_active ? '' : 'text-muted' },
    { label: 'Status', value: row.is_active ? 'Active' : 'Paid' },
  ]);

  mount(app, html`
    ${pageHeader({
      title: record.person_name,
      subtitle: record.description || `${k.noun.charAt(0).toUpperCase()}${k.noun.slice(1)} created ${new Date(record.created_at).toLocaleDateString()}`,
      back: { href: kind === 'loans' ? '/loans/index' : '/debts/index', label: k.plural },
    })}
    <div data-figures>${figures(record)}</div>
    <div data-payments></div>`);

  const refresh = async () => {
    const fresh = await getData(`/${kind}/${id}`);
    mount(app.querySelector('[data-figures]'), figures(fresh));
  };

  const holder = app.querySelector('[data-payments]');
  await listPage({
    root: holder,
    resource: k.paymentsKey,
    listPath: `/${kind}/${id}/payments`,
    title: 'Payments',
    columns: k.paymentColumns,
    newLabel: 'New payment',
    localFilter: true,
    total: true,
    placeholder: 'Search description or amount…',
    ctx: { parentKey: k.parentKey, parentId: Number(id) },
    afterChange: refresh,
  });
}
