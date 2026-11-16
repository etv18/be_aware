// Withdrawals (bank -> cash) and deposits (cash -> bank): the same page with other words. (templates/withdrawals.html, deposits.html)
import { useState } from 'react';

import { YearlyChart } from '@/components/charts/YearlyChart';
import { useToast } from '@/components/Providers';
import { AmountField, DateField, FormDialog, SelectField, TextField } from '@/components/ui/form';
import { PageHeader, StatRow, totalStat } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud } from '@/lib/crud';
import { formatDate, idOrNull, money, toInputValue } from '@/lib/format';
import { useOptions, usePageTitle, useSave } from '@/lib/queries';
import type { CashMovement } from '@/types';

type Kind = {
  path: '/withdrawals' | '/deposits'; noun: string; title: string; subtitle: string; fallback: string;
  accountHeader: string; accountLabel: string; undo: string; chartTitle: string; color: string;
};

const WITHDRAWALS: Kind = {
  path: '/withdrawals', noun: 'withdrawal', title: 'Withdrawals', subtitle: 'Money you took out of a bank account as cash.', fallback: 'Withdrawal',
  accountHeader: 'From account', accountLabel: 'Withdraw from', undo: 'The money goes back to the bank account.', chartTitle: 'Withdrawals per month', color: 'c-withdrawals',
};
const DEPOSITS: Kind = {
  path: '/deposits', noun: 'deposit', title: 'Deposits', subtitle: 'Cash you put into a bank account.', fallback: 'Deposit',
  accountHeader: 'Into account', accountLabel: 'Deposit into', undo: 'The money goes back to cash.', chartTitle: 'Deposits per month', color: 'c-deposits',
};

type Values = { amount: string; description: string; created_at: string; bank_account_id: string };

function MovementForm({ kind, record, onClose }: { kind: Kind; record: CashMovement | null; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave(kind.path);
  const { toast } = useToast();
  const [values, setValues] = useState<Values>(() => record
    ? { amount: record.amount, description: record.description ?? '', created_at: toInputValue(record.created_at), bank_account_id: String(record.bank_account_id ?? '') }
    : { amount: '', description: '', created_at: toInputValue(), bank_account_id: '' });
  const set = (key: keyof Values) => (value: string) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({
      id: record?.id,
      body: { amount: values.amount, bank_account_id: idOrNull(values.bank_account_id), description: values.description || null, created_at: values.created_at || null },
    });
    toast(`${kind.noun.charAt(0).toUpperCase()}${kind.noun.slice(1)} ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={`${record ? 'Edit' : 'New'} ${kind.noun}`} onClose={onClose} onSubmit={submit}>
      <AmountField value={values.amount} onChange={set('amount')} />
      <DateField value={values.created_at} onChange={set('created_at')} />
      <SelectField name="bank_account_id" label={kind.accountLabel} blank="Choose an account" value={values.bank_account_id} onChange={set('bank_account_id')}
        items={(options?.bank_accounts ?? []).map((a) => ({ id: a.id, label: a.nick_name }))} />
      <TextField name="description" label="Description" optional value={values.description} onChange={set('description')} />
    </FormDialog>
  );
}

function CashMovements({ kind }: { kind: Kind }) {
  usePageTitle(kind.title);
  const { rows, meta, filters, onFilters, editing, setEditing, onDelete } = useCrud<CashMovement>({ path: kind.path, noun: kind.noun, undo: kind.undo });

  return (
    <>
      <PageHeader title={kind.title} subtitle={kind.subtitle} newLabel={`New ${kind.noun}`} onNew={() => setEditing('new')} />
      <StatRow stats={[totalStat(meta)]} />

      <TableCard
        headers={[['Description', ''], [kind.accountHeader, 'hidden sm:table-cell'], ['Date', 'hidden sm:table-cell'], ['Amount', 'text-right']]}
        placeholder="Search description or account…"
        count={rows.length} filters={filters} onFilters={onFilters}
      >
        {rows.map((row) => (
          <tr key={row.id}>
            <td className="max-w-[22ch] sm:max-w-[34ch]">
              <span className="block truncate font-medium">{row.description || kind.fallback}</span>
              <span className="block truncate text-xs text-muted sm:hidden">{[row.bank_account_name, formatDate(row.created_at)].filter(Boolean).join(' · ')}</span>
            </td>
            <td className="hidden sm:table-cell">{row.bank_account_name || '–'}</td>
            <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDate(row.created_at)}</td>
            <td className="num text-right font-medium">{money(row.amount)}</td>
            <RowActions onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      <YearlyChart title={kind.chartTitle} model={kind.noun + 's'} label={kind.title} color={kind.color} />

      {editing && <MovementForm key={editing === 'new' ? 'new' : editing.id} kind={kind} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
    </>
  );
}

export const Withdrawals = () => <CashMovements kind={WITHDRAWALS} />;
export const Deposits = () => <CashMovements kind={DEPOSITS} />;
