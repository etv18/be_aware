// One debt: its figures and its payments. Markup: templates/debt.html. (loan.js is the same page for a loan.)
import { $, api, bindList, formatDate, money, setStats, source, toastError } from './common.js';
import { paymentForm } from './forms.js';

const id = $('#page').dataset.id;
let debt = null;

async function showDebt() {
  debt = (await api.get(`/debts/${id}`)).data;
  $('[data-page-title]').textContent = debt.person_name;
  $('[data-page-subtitle]').textContent = debt.description || `Debt created ${new Date(debt.created_at).toLocaleDateString()}`;
  setStats({
    amount: money(debt.amount),
    paid: money(debt.total_paid),
    remaining: money(debt.remaining_amount),
    status: debt.is_active ? 'Active' : 'Paid',
  });
}

const payment = paymentForm({ kind: 'debt', onSaved: () => { list.reload(); showDebt().catch(toastError); } });

const list = bindList({
  path: `/debts/${id}/payments`,
  recordPath: '/debt_payments',
  localFilter: true, // the payments of one debt are few: search them in the browser
  noun: 'payment',
  form: { open: (row) => (row ? payment.edit(row) : payment.create(debt)) },
  onDeleted: () => showDebt().catch(toastError),
  empty: { text: 'No payments yet.' },
  cells: (row) => ({ date: formatDate(row.created_at), source: source(row), amount: money(row.amount) }),
});

showDebt().catch(toastError);
