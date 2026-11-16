// The forms that more than one page uses. (partials/dialogs.html + static/js/forms.js)
//   <TransferForm from={account} onClose={...} />      move money between two accounts
//   <CardPaymentForm card={card} onClose={...} />      pay a card, or add cashback
//   <PaymentForm kind="loan" parentId={3} record={null} onClose={...} />   a payment on a loan or a debt (new when record is null)
import { useState } from 'react';

import { useToast } from '@/components/Providers';
import { AmountField, DateField, FormDialog, MethodField, SelectField, SwitchField } from '@/components/ui/form';
import { idOrNull, toInputValue } from '@/lib/format';
import { useOptions, useSave } from '@/lib/queries';
import type { BankAccount, CreditCard, Payment } from '@/types';

const accounts = (list: BankAccount[] | undefined) => (list ?? []).map((a) => ({ id: a.id, label: a.nick_name }));

export function TransferForm({ from, onClose }: { from: BankAccount; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave('/bank_transfers');
  const { toast } = useToast();
  const [values, setValues] = useState({ amount: '', created_at: toInputValue(), to_bank_account_id: '' });
  const set = (key: keyof typeof values) => (value: string) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({ body: { amount: values.amount, created_at: values.created_at || null, to_bank_account_id: idOrNull(values.to_bank_account_id), from_bank_account_id: from.id } });
    toast('Transfer created.');
    onClose();
  }

  return (
    <FormDialog open title={`Transfer from ${from.nick_name}`} onClose={onClose} onSubmit={submit}>
      <AmountField value={values.amount} onChange={set('amount')} />
      <DateField value={values.created_at} onChange={set('created_at')} />
      <SelectField name="to_bank_account_id" label="To account" blank="Choose an account" value={values.to_bank_account_id} onChange={set('to_bank_account_id')} items={accounts(options?.bank_accounts)} />
    </FormDialog>
  );
}

export function CardPaymentForm({ card, onClose }: { card: CreditCard; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave('/credit_card_payments');
  const { toast } = useToast();
  const [values, setValues] = useState({ amount: '', created_at: toInputValue(), is_cashback: false, bank_account_id: '' });
  const set = <K extends keyof typeof values>(key: K) => (value: (typeof values)[K]) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({
      body: {
        amount: values.amount, is_cashback: values.is_cashback, created_at: values.created_at || null,
        bank_account_id: values.is_cashback ? null : idOrNull(values.bank_account_id), credit_card_id: card.id,
      },
    });
    toast('Payment created.');
    onClose();
  }

  return (
    <FormDialog open title={`Pay ${card.nick_name}`} onClose={onClose} onSubmit={submit}>
      <AmountField value={values.amount} onChange={set('amount')} />
      <DateField value={values.created_at} onChange={set('created_at')} />
      <SwitchField name="is_cashback" label="Cashback" help="Credit added to the card without paying from an account." value={values.is_cashback} onChange={set('is_cashback')} />
      {!values.is_cashback && (
        <SelectField name="bank_account_id" label="Pay from" blank="Choose an account" value={values.bank_account_id} onChange={set('bank_account_id')} items={accounts(options?.bank_accounts)} />
      )}
    </FormDialog>
  );
}

type Method = 'cash' | 'bank';

export function PaymentForm({ kind, parentId, record, onClose }: { kind: 'loan' | 'debt'; parentId: number; record: Payment | null; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave(`/${kind}_payments`);
  const { toast } = useToast();
  const [values, setValues] = useState(() => record
    ? { amount: record.amount, created_at: toInputValue(record.created_at), method: (record.is_cash ? 'cash' : 'bank') as Method, bank_account_id: String(record.bank_account_id ?? '') }
    : { amount: '', created_at: toInputValue(), method: 'cash' as Method, bank_account_id: '' });
  const set = <K extends keyof typeof values>(key: K) => (value: (typeof values)[K]) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({
      id: record?.id,
      body: {
        amount: values.amount, is_cash: values.method === 'cash', created_at: values.created_at || null,
        bank_account_id: values.method === 'bank' ? idOrNull(values.bank_account_id) : null,
        ...(record ? {} : { [`${kind}_id`]: parentId }),
      },
    });
    toast(`Payment ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={`${record ? 'Edit' : 'New'} ${kind} payment`} onClose={onClose} onSubmit={submit}>
      <AmountField value={values.amount} onChange={set('amount')} />
      <DateField value={values.created_at} onChange={set('created_at')} />
      <MethodField<Method> label={kind === 'loan' ? 'Received in' : 'Paid from'} value={values.method} onChange={set('method')} options={[['cash', 'Cash'], ['bank', 'Bank account']]} />
      {values.method === 'bank' && (
        <SelectField name="bank_account_id" label="Bank account" blank="Choose an account" value={values.bank_account_id} onChange={set('bank_account_id')} items={accounts(options?.bank_accounts)} />
      )}
    </FormDialog>
  );
}
