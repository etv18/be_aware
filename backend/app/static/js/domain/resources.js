// One entry per kind of record: where it lives in the API, how it is edited and what to tell the person.
// manager(key, {onChange}) turns an entry into create / edit / remove actions with dialogs and toasts.
import { api, invalidateOptions, loadOptions } from '../core/api.js';
import { openForm } from '../core/form.js';
import { confirmDialog, toast, toastError } from '../core/ui.js';
import * as forms from './forms.js';

export const RESOURCES = {
  expenses: { path: '/expenses', noun: 'expense', form: forms.expense, undo: 'The money goes back to where it came from.' },
  incomes: { path: '/incomes', noun: 'income', form: forms.income },
  withdrawals: { path: '/withdrawals', noun: 'withdrawal', form: forms.withdrawal, undo: 'The money goes back to the bank account.' },
  deposits: { path: '/deposits', noun: 'deposit', form: forms.deposit, undo: 'The money goes back to cash.' },
  loans: { path: '/loans', noun: 'loan', form: forms.loan, undo: 'Its payments are removed too.' },
  debts: { path: '/debts', noun: 'debt', form: forms.debt, undo: 'Its payments are removed too.' },
  'loan-payments': { path: '/loan_payments', noun: 'payment', form: forms.loanPayment },
  'debt-payments': { path: '/debt_payments', noun: 'payment', form: forms.debtPayment },
  'bank-transfers': { path: '/banktransfer', noun: 'transfer', form: forms.bankTransfer, undo: 'Both balances go back as they were.' },
  'credit-card-payments': { path: '/credit_card_payments', noun: 'payment', form: forms.creditCardPayment },
  banks: { path: '/banks', noun: 'bank', form: forms.bank, refreshOptions: true },
  'bank-accounts': { path: '/bank_accounts', noun: 'bank account', form: forms.bankAccount, refreshOptions: true, undo: 'It is hidden; its history stays.' },
  'credit-cards': { path: '/credit_cards', noun: 'credit card', form: forms.creditCard, refreshOptions: true, undo: 'It is hidden; its history stays.' },
  'expense-categories': { path: '/expense_categories', noun: 'category', form: forms.expenseCategory, refreshOptions: true, undo: 'It is hidden; its expenses stay.' },
  'cash-adjustments': { path: '/cashledger', noun: 'adjustment', form: forms.cashAdjustment },
};

/**
 * Actions for one kind of record.
 *   const records = manager('expenses', { onChange: reload, ctx: {...} })
 *   records.create(); records.edit(row); records.remove(row)
 * ctx is handed to the form definition (e.g. the loan a payment belongs to).
 */
export function manager(key, { onChange = () => {}, ctx = {} } = {}) {
  const resource = RESOURCES[key];

  async function save(row) {
    if (resource.refreshOptions) invalidateOptions();
    const options = await loadOptions();
    const definition = resource.form(options, ctx);

    const saved = await openForm({
      title: definition.title(row),
      fields: definition.fields,
      values: row ? definition.fromRecord(row) : definition.defaults(),
      toBody: definition.toBody,
      record: row,
      onSubmit: (body) => (row ? api.put(`${resource.path}/${row.id}`, body) : api.post(resource.path, body)),
    });

    if (saved) {
      if (resource.refreshOptions) invalidateOptions();
      toast(row ? `${capitalize(resource.noun)} updated.` : `${capitalize(resource.noun)} created.`);
      onChange(saved);
    }
    return saved;
  }

  return {
    create: () => save(null).catch(toastError),
    edit: (row) => save(row).catch(toastError),
    async remove(row) {
      const confirmed = await confirmDialog({
        title: `Delete this ${resource.noun}?`,
        message: resource.undo || 'This cannot be undone.',
      });
      if (!confirmed) return;
      try {
        await api.delete(`${resource.path}/${row.id}`);
        if (resource.refreshOptions) invalidateOptions();
        toast(`${capitalize(resource.noun)} deleted.`);
        onChange(null);
      } catch (error) {
        toastError(error);
      }
    },
  };
}

const capitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);
