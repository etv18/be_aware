// The expenses page. (templates/expenses.html + static/js/expenses.js)
import { useState } from 'react';

import { YearlyChart } from '@/components/charts/YearlyChart';
import { useToast } from '@/components/Providers';
import { PageHeader, StatRow } from '@/components/ui/page';
import { AmountField, DateField, FormDialog, MethodField, SelectField, TextField } from '@/components/ui/form';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud } from '@/lib/crud';
import { formatDate, idOrNull, money, plural, source, toInputValue } from '@/lib/format';
import { useOptions, usePageTitle, useSave } from '@/lib/queries';
import type { Expense, ExpenseBody, ExpenseListMeta } from '@/types';

type Method = 'cash' | 'bank' | 'card';

/** What the form holds while it is open. Everything is text until it is sent. */
type Values = {
  amount: string; description: string; created_at: string; expense_category_id: string;
  method: Method; bank_account_id: string; credit_card_id: string;
};

const fromRecord = (r: Expense): Values => ({
  amount: r.amount, description: r.description ?? '', created_at: toInputValue(r.created_at),
  expense_category_id: String(r.expense_category_id ?? ''), method: r.is_cash ? 'cash' : r.credit_card_id ? 'card' : 'bank',
  bank_account_id: String(r.bank_account_id ?? ''), credit_card_id: String(r.credit_card_id ?? ''),
});

/** The JSON the server gets. A select left empty goes as null and the server answers which field is missing. */
const toBody = (v: Values): Omit<ExpenseBody, 'expense_category_id'> & { expense_category_id: number | null } => ({
  amount: v.amount,
  description: v.description,
  created_at: v.created_at || null,
  expense_category_id: idOrNull(v.expense_category_id),
  is_cash: v.method === 'cash',
  bank_account_id: v.method === 'bank' ? idOrNull(v.bank_account_id) : null,
  credit_card_id: v.method === 'card' ? idOrNull(v.credit_card_id) : null,
});

// ------------------------------------------------------------------ the new / edit form
function ExpenseForm({ record, onClose }: { record: Expense | null; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave('/expenses');
  const { toast } = useToast();

  const [values, setValues] = useState<Values>(() => record ? fromRecord(record) : {
    amount: '', description: '', method: 'cash', created_at: toInputValue(), expense_category_id: '', bank_account_id: '', credit_card_id: '',
  });
  const set = <K extends keyof Values>(key: K) => (value: Values[K]) => setValues((current) => ({ ...current, [key]: value }));

  // a new expense starts on the first category, like the old form did
  const firstCategory = options?.expense_categories[0]?.id;
  if (!record && values.expense_category_id === '' && firstCategory !== undefined) setValues({ ...values, expense_category_id: String(firstCategory) });

  async function submit() {
    await save.mutateAsync({ id: record?.id, body: toBody(values) });
    toast(`Expense ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={record ? 'Edit expense' : 'New expense'} onClose={onClose} onSubmit={submit}>
      <AmountField value={values.amount} onChange={set('amount')} />
      <DateField value={values.created_at} onChange={set('created_at')} />
      <SelectField name="expense_category_id" label="Category" blank="Choose a category" value={values.expense_category_id} onChange={set('expense_category_id')}
        items={(options?.expense_categories ?? []).map((c) => ({ id: c.id, label: c.display_name }))} />
      <TextField name="description" label="Description" value={values.description} onChange={set('description')} />
      <MethodField<Method> label="Paid with" value={values.method} onChange={set('method')} options={[['cash', 'Cash'], ['bank', 'Bank account'], ['card', 'Credit card']]} />
      {values.method === 'bank' && (
        <SelectField name="bank_account_id" label="Bank account" blank="Choose an account" value={values.bank_account_id} onChange={set('bank_account_id')}
          items={(options?.bank_accounts ?? []).map((a) => ({ id: a.id, label: a.nick_name }))} />
      )}
      {values.method === 'card' && (
        <SelectField name="credit_card_id" label="Credit card" blank="Choose a card" value={values.credit_card_id} onChange={set('credit_card_id')}
          items={(options?.credit_cards ?? []).map((c) => ({ id: c.id, label: c.nick_name }))} />
      )}
    </FormDialog>
  );
}

// ------------------------------------------------------------------ the page
export function Expenses() {
  usePageTitle('Expenses');
  const { rows, meta, filters, onFilters, editing, setEditing, onDelete } = useCrud<Expense, ExpenseListMeta>({
    path: '/expenses', noun: 'expense', undo: 'The money goes back to where it came from.',
  });

  return (
    <>
      <PageHeader title="Expenses" subtitle="What you spent, from cash, accounts and cards." newLabel="New expense" onNew={() => setEditing('new')} />

      <StatRow stats={[
        { label: 'Total', value: meta ? money(meta.total) : '–', hint: meta ? `${meta.count} ${plural(meta.count, 'expense')}` : '' },
        { label: 'Category limits', value: meta ? money(meta.budget.limit) : '–' },
        { label: 'Spent', value: meta ? money(meta.budget.spent) : '–' },
        { label: 'Left', value: meta ? money(meta.budget.left) : '–', negative: Number(meta?.budget.left) < 0 },
      ]} />

      <TableCard
        headers={[['Description', ''], ['Category', 'hidden sm:table-cell'], ['Paid with', 'hidden md:table-cell'], ['Date', 'hidden sm:table-cell'], ['Amount', 'text-right']]}
        placeholder="Search description, category, account…"
        note="Showing this month. Search or pick dates to look further back."
        empty={{ text: 'No expenses this month. Use “New expense” to add one.' }}
        count={rows.length} filters={filters} onFilters={onFilters}
      >
        {rows.map((row) => (
          <tr key={row.id}>
            <td className="max-w-[22ch] sm:max-w-[34ch]">
              <span className="block truncate font-medium">{row.description}</span>
              {/* the line under the description on a phone */}
              <span className="block truncate text-xs text-muted sm:hidden">{[row.expense_category_name, formatDate(row.created_at)].filter(Boolean).join(' · ')}</span>
            </td>
            <td className="hidden sm:table-cell"><span className="tag">{row.expense_category_name || '–'}</span></td>
            <td className="hidden md:table-cell">{source(row)}</td>
            <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDate(row.created_at)}</td>
            <td className="num text-right font-medium text-negative">{money(row.amount)}</td>
            <RowActions onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      <YearlyChart title="Expenses per month" model="expenses" label="Expenses" color="c-expenses" />

      {editing && <ExpenseForm key={editing === 'new' ? 'new' : editing.id} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
    </>
  );
}
