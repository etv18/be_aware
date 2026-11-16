// The expense categories page. (templates/expense_categories.html + static/js/expense_categories.js)
import { useState } from 'react';

import { ReportChart } from '@/components/charts/ReportChart';
import { useToast } from '@/components/Providers';
import { AmountField, FormDialog, TextField } from '@/components/ui/form';
import { PageHeader } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud, useOpenRow } from '@/lib/crud';
import { formatDate, money } from '@/lib/format';
import { usePageTitle, useReport, useSave } from '@/lib/queries';
import type { CategoriesMonthly, ExpenseCategory } from '@/types';

function CategoryForm({ record, onClose }: { record: ExpenseCategory | null; onClose: () => void }) {
  const save = useSave('/expense_categories');
  const { toast } = useToast();
  const [values, setValues] = useState({ name: record?.display_name ?? '', limit: record?.limit ?? '0' });

  async function submit() {
    await save.mutateAsync({ id: record?.id, body: { name: values.name, limit: values.limit === '' ? '0' : values.limit } });
    toast(`Category ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={record ? 'Edit category' : 'New category'} onClose={onClose} onSubmit={submit}>
      <TextField name="name" label="Name" help="At least 4 characters." value={values.name} onChange={(name) => setValues({ ...values, name })} />
      <AmountField name="limit" label="Monthly limit" help="Leave 0 for no limit." value={values.limit} onChange={(limit) => setValues({ ...values, limit })} />
    </FormDialog>
  );
}

export function ExpenseCategories() {
  usePageTitle('Expense categories');
  const openRow = useOpenRow();
  const { rows, editing, setEditing, onDelete } = useCrud<ExpenseCategory>({ path: '/expense_categories', noun: 'category', undo: 'It is hidden; its expenses stay.' });
  const spent = useReport<CategoriesMonthly>('/expense_categories/reports/monthly');

  return (
    <>
      <PageHeader title="Expense categories" subtitle="Group your expenses and give each group a monthly limit." newLabel="New category" onNew={() => setEditing('new')} />

      <TableCard headers={[['Category', ''], ['Added', 'hidden sm:table-cell'], ['Monthly limit', 'text-right']]} count={rows.length} openRows>
        {rows.map((row) => (
          <tr key={row.id} {...openRow(`/expense_categories/${row.id}`)}>
            <td><span className="inline-flex items-center gap-2 font-medium"><span className="dot" style={{ background: 'rgb(var(--c-expenses))' }} /><span>{row.display_name}</span></span></td>
            <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDate(row.created_at)}</td>
            <td className={`num text-right font-medium ${Number(row.limit) > 0 ? '' : 'text-muted'}`}>{Number(row.limit) > 0 ? money(row.limit) : 'No limit'}</td>
            <RowActions onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      <ReportChart title="Spent this month, by category"
        options={spent.data ? { type: 'bar', labels: spent.data.names, series: [{ label: 'Spent', data: spent.data.totals, color: 'c-expenses' }] } : null} />

      {editing && <CategoryForm key={editing === 'new' ? 'new' : editing.id} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
    </>
  );
}
