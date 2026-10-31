// One loan: its figures and its payments. Markup: templates/loan.html. (debt.js is the same page for a debt.)
import { $, api, bindList, formatDate, money, setStats, source, toastError } from './common.js';
import { paymentForm } from './forms.js';

const id = $('#page').dataset.id;
let loan = null;

async function showLoan() {
  loan = (await api.get(`/loans/${id}`)).data;
  $('[data-page-title]').textContent = loan.person_name;
  $('[data-page-subtitle]').textContent = loan.description || `Loan created ${new Date(loan.created_at).toLocaleDateString()}`;
  setStats({
    amount: money(loan.amount),
    paid: money(loan.total_paid),
    remaining: money(loan.remaining_amount),
    status: loan.is_active ? 'Active' : 'Paid',
  });
}

const payment = paymentForm({ kind: 'loan', onSaved: () => { list.reload(); showLoan().catch(toastError); } });

const list = bindList({
  path: `/loans/${id}/payments`,
  recordPath: '/loan_payments',
  localFilter: true, // the payments of one loan are few: search them in the browser
  noun: 'payment',
  form: { open: (row) => (row ? payment.edit(row) : payment.create(loan)) },
  onDeleted: () => showLoan().catch(toastError),
  empty: { text: 'No payments yet.' },
  cells: (row) => ({ date: formatDate(row.created_at), source: source(row), amount: money(row.amount) }),
});

showLoan().catch(toastError);
