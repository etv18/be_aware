// The forms that more than one page uses (their markup is partials/dialogs.html). Each one returns something with open(...).
import { $, idOrNull, nowInputValue, recordForm, toInputValue } from './common.js';

/** Transfer between bank accounts. transfer.open(account) opens it with that account as the "from" side. */
export function transferForm({ onSaved }) {
  let from = null;
  const form = recordForm($('#transfer-dialog'), {
    path: '/bank_transfers',
    noun: 'transfer',
    title: () => `Transfer from ${from.nick_name}`,
    selects: { to_bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'] },
    defaults: () => ({ created_at: nowInputValue(), to_bank_account_id: '' }),
    toBody: (v) => ({ amount: v.amount, to_bank_account_id: idOrNull(v.to_bank_account_id), created_at: v.created_at || null, from_bank_account_id: from.id }),
    onSaved,
  });
  return { open: (account) => { from = account; return form.open(); } };
}

/** Pay a credit card. payment.open(card) opens it for that card. */
export function cardPaymentForm({ onSaved }) {
  let card = null;
  const form = recordForm($('#card-payment-dialog'), {
    path: '/credit_card_payments',
    noun: 'payment',
    title: () => `Pay ${card.nick_name}`,
    selects: { bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'] },
    defaults: () => ({ created_at: nowInputValue(), is_cashback: false, bank_account_id: '' }),
    toBody: (v) => ({
      amount: v.amount, is_cashback: v.is_cashback, created_at: v.created_at || null,
      bank_account_id: v.is_cashback ? null : idOrNull(v.bank_account_id), credit_card_id: card.id,
    }),
    onSaved,
  });
  return { open: (cardRow) => { card = cardRow; return form.open(); } };
}

/**
 * A payment on a loan or a debt (kind: 'loan' | 'debt').
 *   payment.create(parent) opens it for that loan / debt · payment.edit(paymentRow) edits a payment
 */
export function paymentForm({ kind, onSaved }) {
  let parent = null;
  const form = recordForm($('#payment-dialog'), {
    path: `/${kind}_payments`,
    noun: 'payment',
    title: (record) => `${record ? 'Edit' : 'New'} ${kind} payment`,
    selects: { bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'] },
    defaults: () => ({ method: 'cash', created_at: nowInputValue(), bank_account_id: '' }),
    fromRecord: (r) => ({ amount: r.amount, created_at: toInputValue(r.created_at), method: r.is_cash ? 'cash' : 'bank', bank_account_id: r.bank_account_id ?? '' }),
    toBody: (v, record) => ({
      amount: v.amount, is_cash: v.method === 'cash', created_at: v.created_at || null,
      bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
      ...(record ? {} : { [`${kind}_id`]: parent.id }),
    }),
    onSaved,
  });
  return {
    create: (parentRow) => { parent = parentRow; return form.open(null); },
    edit: (payment) => form.open(payment),
  };
}
