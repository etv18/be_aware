// The incomes page. (templates/incomes.html + static/js/incomes.js)
import { useState } from 'react';

import { YearlyChart } from '@/components/charts/YearlyChart';
import { useToast } from '@/components/Providers';
import { AmountField, DateField, FormDialog, MethodField, SelectField, TextField } from '@/components/ui/form';
import { PageHeader, StatRow, totalStat } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud } from '@/lib/crud';
import { formatDate, idOrNull, money, source, toInputValue } from '@/lib/format';
import { useOptions, usePageTitle, useSave } from '@/lib/queries';
import type { Income } from '@/types';

type Method = 'cash' | 'bank';
type Values = { amount: string; description: string; created_at: string; method: Method; bank_account_id: string };

function IncomeForm({ record, onClose }: { record: Income | null; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave('/incomes');
  const { toast } = useToast();
  const [values, setValues] = useState<Values>(() => record
    ? { amount: record.amount, description: record.description ?? '', created_at: toInputValue(record.created_at), method: record.is_cash ? 'cash' : 'bank', bank_account_id: String(record.bank_account_id ?? '') }
    : { amount: '', description: '', method: 'cash', created_at: toInputValue(), bank_account_id: '' });
  const set = <K extends keyof Values>(key: K) => (value: Values[K]) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({
      id: record?.id,
      body: {
        amount: values.amount, description: values.description || null, created_at: values.created_at || null,
        is_cash: values.method === 'cash', bank_account_id: values.method === 'bank' ? idOrNull(values.bank_account_id) : null,
      },
    });
    toast(`Income ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={record ? 'Edit income' : 'New income'} onClose={onClose} onSubmit={submit}>
      <AmountField value={values.amount} onChange={set('amount')} />
      <DateField value={values.created_at} onChange={set('created_at')} />
      <TextField name="description" label="Description" optional value={values.description} onChange={set('description')} />
      <MethodField<Method> label="Received in" value={values.method} onChange={set('method')} options={[['cash', 'Cash'], ['bank', 'Bank account']]} />
      {values.method === 'bank' && (
        <SelectField name="bank_account_id" label="Bank account" blank="Choose an account" value={values.bank_account_id} onChange={set('bank_account_id')}
          items={(options?.bank_accounts ?? []).map((a) => ({ id: a.id, label: a.nick_name }))} />
      )}
    </FormDialog>
  );
}

export function Incomes() {
  usePageTitle('Incomes');
  const { rows, meta, filters, onFilters, editing, setEditing, onDelete } = useCrud<Income>({ path: '/incomes', noun: 'income' });

  return (
    <>
      <PageHeader title="Incomes" subtitle="What came in, as cash or into an account." newLabel="New income" onNew={() => setEditing('new')} />
      <StatRow stats={[totalStat(meta)]} />

      <TableCard
        headers={[['Description', ''], ['Received in', 'hidden md:table-cell'], ['Date', 'hidden sm:table-cell'], ['Amount', 'text-right']]}
        placeholder="Search description or account…"
        note="Showing this month. Search or pick dates to look further back."
        empty={{ text: 'No incomes this month. Use “New income” to add one.' }}
        count={rows.length} filters={filters} onFilters={onFilters}
      >
        {rows.map((row) => (
          <tr key={row.id}>
            <td className="max-w-[22ch] sm:max-w-[34ch]">
              <span className="block truncate font-medium">{row.description || 'No description'}</span>
              <span className="block truncate text-xs text-muted sm:hidden">{`${source(row)} · ${formatDate(row.created_at)}`}</span>
            </td>
            <td className="hidden md:table-cell">{source(row)}</td>
            <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDate(row.created_at)}</td>
            <td className="num text-right font-medium text-positive">{money(row.amount)}</td>
            <RowActions onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      <YearlyChart title="Income per month" model="incomes" label="Income" color="c-incomes" />

      {editing && <IncomeForm key={editing === 'new' ? 'new' : editing.id} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
    </>
  );
}
