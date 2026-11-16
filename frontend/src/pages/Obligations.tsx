// Loans (money you lent) and debts (money you owe): the same page with other words. (templates/loans.html, debts.html)
import { useState } from 'react';
import { Link } from 'react-router-dom';

import { YearlyChart } from '@/components/charts/YearlyChart';
import { Icon } from '@/components/Icon';
import { PaymentForm } from '@/components/forms/shared';
import { useToast } from '@/components/Providers';
import { AmountField, DateField, FormDialog, MethodField, SelectField, SwitchField, TextField } from '@/components/ui/form';
import { PageHeader, StatRow } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud, useOpenRow } from '@/lib/crud';
import { formatDate, idOrNull, money, source, toInputValue } from '@/lib/format';
import { useOptions, usePageTitle, useSave } from '@/lib/queries';
import type { Debt, Loan } from '@/types';

type Record = Loan | Debt;
type Method = 'cash' | 'bank' | 'card' | 'none';
type Meta = { count: number; remaining: string; actives?: number; active?: number; paids?: number; paid?: number };

export type Kind = {
  kind: 'loan' | 'debt'; path: '/loans' | '/debts'; title: string; subtitle: string; remainingLabel: string;
  sourceLabel: string; methods: [Method, string][]; methodHelp: string; markPaidHelp: string;
  openLabel: string; openClass: string; payLabel: string; color: string; paymentsPath: string;
};

export const LOANS: Kind = {
  kind: 'loan', path: '/loans', title: 'Loans', subtitle: 'Money you lent. Payments you receive reduce what is left.', remainingLabel: 'Still to collect',
  sourceLabel: 'Lent from', methods: [['cash', 'Cash'], ['bank', 'Bank account'], ['card', 'Credit card'], ['none', 'No money']],
  methodHelp: 'Pick "No money" when you paid for something in kind and no money left your hands.',
  markPaidHelp: 'The person owes you nothing more, even if the payments do not cover the amount.',
  openLabel: 'COLLECT', openClass: 'tag-warning', payLabel: 'Receive a payment', color: 'c-loans', paymentsPath: '/loan_payments',
};
export const DEBTS: Kind = {
  kind: 'debt', path: '/debts', title: 'Debts', subtitle: 'Money you owe. Payments you make reduce what is left.', remainingLabel: 'Still to pay',
  sourceLabel: 'Received in', methods: [['cash', 'Cash'], ['bank', 'Bank account'], ['none', 'No money']],
  methodHelp: 'Pick "No money" when someone paid for something in kind and you never received the money.',
  markPaidHelp: 'You owe nothing more, even if the payments do not cover the amount.',
  openLabel: 'ACTIVE', openClass: 'tag-negative', payLabel: 'Make a payment', color: 'c-debts', paymentsPath: '/debt_payments',
};

type Values = {
  person_name: string; amount: string; description: string; created_at: string; method: Method;
  bank_account_id: string; credit_card_id: string; mark_paid: boolean;
};

const methodOf = (r: Record): Method => (r.is_cash ? 'cash' : 'credit_card_id' in r && r.credit_card_id ? 'card' : r.bank_account_id ? 'bank' : 'none');

function ObligationForm({ k, record, onClose }: { k: Kind; record: Record | null; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave(k.path);
  const { toast } = useToast();
  const [values, setValues] = useState<Values>(() => record
    ? {
      person_name: record.person_name, amount: record.amount, description: record.description ?? '', created_at: toInputValue(record.created_at), method: methodOf(record),
      bank_account_id: String(record.bank_account_id ?? ''), credit_card_id: String('credit_card_id' in record ? record.credit_card_id ?? '' : ''), mark_paid: !record.is_active,
    }
    : { person_name: '', amount: '', description: '', created_at: toInputValue(), method: 'cash', bank_account_id: '', credit_card_id: '', mark_paid: false });
  const set = <K extends keyof Values>(key: K) => (value: Values[K]) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({
      id: record?.id,
      body: {
        person_name: values.person_name, amount: values.amount, description: values.description || null, created_at: values.created_at || null,
        is_cash: values.method === 'cash',
        bank_account_id: values.method === 'bank' ? idOrNull(values.bank_account_id) : null,
        ...(k.kind === 'loan' ? { credit_card_id: values.method === 'card' ? idOrNull(values.credit_card_id) : null } : {}),
        ...(record ? { is_active: !values.mark_paid } : {}), // only when editing: "mark as paid" closes it by hand
      },
    });
    toast(`${k.kind === 'loan' ? 'Loan' : 'Debt'} ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={`${record ? 'Edit' : 'New'} ${k.kind}`} onClose={onClose} onSubmit={submit}>
      <TextField name="person_name" label="Person" half value={values.person_name} onChange={set('person_name')} />
      <AmountField value={values.amount} onChange={set('amount')} />
      <DateField value={values.created_at} onChange={set('created_at')} />
      <TextField name="description" label="Description" optional value={values.description} onChange={set('description')} />
      <MethodField<Method> label={k.sourceLabel} value={values.method} onChange={set('method')} options={k.methods} help={k.methodHelp} />
      {values.method === 'bank' && (
        <SelectField name="bank_account_id" label="Bank account" blank="Choose an account" value={values.bank_account_id} onChange={set('bank_account_id')}
          items={(options?.bank_accounts ?? []).map((a) => ({ id: a.id, label: a.nick_name }))} />
      )}
      {values.method === 'card' && (
        <SelectField name="credit_card_id" label="Credit card" blank="Choose a card" value={values.credit_card_id} onChange={set('credit_card_id')}
          items={(options?.credit_cards ?? []).map((c) => ({ id: c.id, label: c.nick_name }))} />
      )}
      {record && <SwitchField name="mark_paid" label="Mark as paid" help={k.markPaidHelp} value={values.mark_paid} onChange={set('mark_paid')} />}
    </FormDialog>
  );
}

function Obligations({ k }: { k: Kind }) {
  usePageTitle(k.title);
  const openRow = useOpenRow();
  const { rows, meta, filters, onFilters, editing, setEditing, onDelete } = useCrud<Record, Meta>({ path: k.path, noun: k.kind, undo: 'Its payments are removed too.' });
  const [paying, setPaying] = useState<Record | null>(null);
  const noun = k.kind === 'loan' ? 'loan' : 'debt';

  return (
    <>
      <PageHeader title={k.title} subtitle={k.subtitle} newLabel={`New ${noun}`} onNew={() => setEditing('new')}>
        <Link to={k.paymentsPath} className="btn btn-outline"><Icon name="list" />All payments</Link>
      </PageHeader>

      <StatRow stats={[
        { label: k.remainingLabel, value: meta ? money(meta.remaining) : '–' },
        { label: 'Active', value: meta ? (meta.actives ?? meta.active ?? 0) : '–' },
        { label: 'Paid', value: meta ? (meta.paids ?? meta.paid ?? 0) : '–' },
      ]} />

      <TableCard
        headers={[['Person', ''], ['Status', 'hidden sm:table-cell'], [k.sourceLabel, 'hidden md:table-cell'], ['Date', 'hidden lg:table-cell'], ['Paid', 'hidden md:table-cell text-right'], ['Remaining', 'text-right'], ['Amount', 'hidden sm:table-cell text-right']]}
        placeholder="Search person, description, account…"
        count={rows.length} filters={filters} onFilters={onFilters} openRows
      >
        {rows.map((row) => (
          <tr key={row.id} {...openRow(`${k.path}/${row.id}`)}>
            <td>
              <span className="block font-medium">{row.person_name}</span>
              {row.description && <span className="block max-w-[28ch] truncate text-xs text-muted">{row.description}</span>}
            </td>
            <td className="hidden sm:table-cell"><span className={`tag ${row.is_active ? k.openClass : 'tag-positive'}`}>{row.is_active ? k.openLabel : 'Paid'}</span></td>
            <td className="hidden md:table-cell">{source(row)}</td>
            <td className="hidden whitespace-nowrap text-muted lg:table-cell">{formatDate(row.created_at)}</td>
            <td className="num hidden text-right md:table-cell">{money(row.total_paid)}</td>
            <td className={`num text-right ${row.is_active ? 'font-medium' : 'text-muted'}`}>{money(row.remaining_amount)}</td>
            <td className="num hidden text-right font-medium sm:table-cell">{money(row.amount)}</td>
            <RowActions extra={row.is_active ? [{ icon: 'hand-coins', label: k.payLabel, onClick: () => setPaying(row) }] : []} onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      <YearlyChart title={`${k.title} per month`} model={k.path.slice(1)} label={k.title} color={k.color} />

      {editing && <ObligationForm key={editing === 'new' ? 'new' : editing.id} k={k} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
      {paying && <PaymentForm kind={k.kind} parentId={paying.id} record={null} onClose={() => setPaying(null)} />}
    </>
  );
}

export const Loans = () => <Obligations k={LOANS} />;
export const Debts = () => <Obligations k={DEBTS} />;
